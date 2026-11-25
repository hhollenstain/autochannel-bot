I've read the frontend, its existing tests and the CI setup, and now I'm writing the spec.

# Local browser UI tests with mocked services and screenshots for LBW

## Problem
The only frontend tests today are the Vitest + jsdom tests in `frontend/src/App.test.tsx`. They never render the real page in a browser, so they can't show what the UI looks like. LBW needs a local command that runs the built SPA in a real browser and saves screenshots of each screen. That command must work without the Flask API on :5000, Discord OAuth, a database, or any internet access.

## Requirements
- R1: A new npm script in `frontend/package.json` (proposed: `test:e2e`) starts the Vite app and runs browser tests against it with Playwright. These tests live outside `src/`, in a new folder such as `frontend/e2e/`.
- R2: The browser tests mock every `/api/*` request inside the browser. The mocks cover `GET /api/me`, `GET /api/guilds/:guildId` and `PATCH /api/guilds/:guildId/categories/:categoryId`, and their response shapes match the types in `frontend/src/api.ts`. The tests pass with nothing listening on :5000.
- R3: The tests fulfill or block every request to an outside origin, so a run sends no traffic outside localhost. This covers Google Fonts in `frontend/index.html` and guild/avatar icon URLs. Mock guild and user icons point to local files in `frontend/public/img/`.
- R4: The tests cover these screens and states, and each one checks at least one visible element:
  - Home (`/`) and Instructions (`/instructions`).
  - Dashboard logged out (`/api/me` returns 401, and the page shows a "Login" link).
  - Dashboard logged in, with the server list.
  - Guild categories (`/dashboard/:guildId`) on the default tab and on the "Custom Channels" tab.
  - Guild categories when the bot isn't in the server (409 with `invite_url`, showing the "Add Auto-chan to …" link).
  - Guild added (`/guild-added/:guildId`).
  - Not Found (an unknown path).
- R5: Each screen in R4 saves a full-page PNG with a stable, descriptive name (e.g. `dashboard-logged-in.png`) into one known folder (proposed: `frontend/e2e/screenshots/`). Each run replaces the files from the last run. The folder is listed in `.gitignore`.
- R6: The existing `npm test` (Vitest) does not pick up the Playwright test files. `npm run typecheck`, `npm test` and `npm run build` still pass unchanged.
- R7: The `justfile` gets a recipe for the new tests (proposed: `just e2e`). The README "Development" section documents that recipe, the one-time browser install step, and where the screenshots go.

## Acceptance criteria
- [ ] Nothing runs on :5000 and the network is offline apart from localhost. `cd frontend && npm run test:e2e` exits 0, and every test listed in R4 is reported as passed. (R1, R2, R3, R4)
- [ ] A test-level guard fails the run if any request to a non-localhost origin isn't fulfilled or aborted by the mocks. A run produces no such failures. (R3)
- [ ] After a run, `frontend/e2e/screenshots/` holds one non-empty PNG per screen in R4. Opening them shows the rendered pages: server name "Planet Express"-style mock data, the category table, and the invite link. They don't show blank pages or error states. (R4, R5)
- [ ] Running the command twice leaves the same set of file names, with no duplicates or stale extras. `git status` doesn't list the screenshots. (R5)
- [ ] `npm test` still runs only `src/**` tests and reports the same 7 tests in `App.test.tsx` as passing. `npm run typecheck` and `npm run build` exit 0. (R6)
- [ ] `just e2e` runs the same suite, and the README describes the browser install, the command, and the screenshot location. (R7)

## Out of scope
- Comparing screenshots against stored baselines (pixel-diff / visual regression assertions).
- Adding the browser tests or screenshot uploads to `.github/workflows/ci.yml`.
- Testing the Flask backend, the real Discord OAuth `/login` and `/logout` redirects, or the database.
- Changing any app code in `frontend/src/` beyond what testability strictly needs.
- Rewriting or moving the existing Vitest tests.

## Open questions
- Should one browser (Chromium) and one desktop viewport be enough, or does LBW also want mobile-viewport screenshots of each screen?
- Should the tests run against `vite dev` (faster) or `vite build` + `vite preview` (closer to production)? The proposed default is `vite preview` after a build.
- Is `frontend/e2e/screenshots/` the right place for LBW to collect screenshots, or does LBW expect a specific path or an env var override (e.g. `SCREENSHOT_DIR`)?
- Should the mock data be shared with `App.test.tsx` (the `GUILD`, `ME` and `CATEGORY` objects), or kept separately in the e2e folder?
