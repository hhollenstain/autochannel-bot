# autochannel-ui

Web dashboard for the AutoChannel Discord bot: log in with Discord, pick a server,
and configure which categories Auto-chan manages.

## Layout

```
autochannel/               Flask JSON API + Discord OAuth redirects; serves the built SPA
frontend/                  React + TypeScript (Vite) single-page app
packages/autochannel-db/   Shared SQLAlchemy models + Alembic migrations
tests/                     Backend pytest suite
```

`packages/autochannel-db` is the only place the schema is defined. It is plain
SQLAlchemy (no Flask) and supports Python >= 3.10 so `autochannel-bot` can depend on it
directly instead of keeping its own copy of `models.py` in sync.

## Development

Requires Python 3.14 + [uv](https://docs.astral.sh/uv/) and Node 22+. Recipes live in the
`Makefile` (`make help` lists them).

```sh
make install          # uv sync + npm ci
make api              # Flask API on :5000 (needs the env vars from .env.example)
make web              # Vite dev server on :5173, proxies /api, /login, /logout to :5000
make test             # pytest + frontend typecheck/tests
make e2e              # Playwright browser tests with mocked /api; screenshots → frontend/e2e/screenshots/
make migrate          # alembic upgrade head against $SQLALCHEMY_DATABASE_URI
```

Browser tests (`frontend/e2e/`):

- Install Chromium once: `cd frontend && npx playwright install chromium`.
- `make e2e` (or `cd frontend && npm run test:e2e`) builds the SPA, serves it with
  `vite preview` on :4173, and drives it in headless Chromium. Every `/api/*` call is mocked
  in the browser and outside requests (Google Fonts) are stubbed, so no API on :5000, Discord
  login, database or internet access is needed. Any unmocked request fails the test.
- Each screen saves a full-page PNG to `frontend/e2e/screenshots/` (override with
  `SCREENSHOT_DIR`). The folder is cleared at the start of each run and is git-ignored.

For local OAuth via the Vite server set `FRONTEND_URL=http://localhost:5173` so the API
redirects back to it after login.

`make docker-compose` builds the image (frontend is compiled in a Node build stage) and
runs it with secrets from 1Password.

## Migrations

```sh
uv run alembic -c packages/autochannel-db/alembic.ini upgrade head
uv run alembic -c packages/autochannel-db/alembic.ini revision --autogenerate -m "..."
```

Revision ids are the same ones Flask-Migrate created, so existing databases upgrade in
place.

`tests/test_migrations.py` fails if `models.py` and the migration history disagree. It
needs an empty Postgres in `TEST_DATABASE_URI`; CI (`.github/workflows/ci.yml`) provides
one.

## Merging into the autochannel-bot monorepo

The repo is already a uv workspace, which makes the move mostly mechanical:

1. Move this app under e.g. `apps/ui/` (`autochannel/`, `frontend/`, `tests/`, its
   `pyproject.toml`) and add the bot as `apps/bot/`.
2. Move `packages/autochannel-db` to the monorepo root `packages/` and make the root
   `pyproject.toml` a virtual workspace with `members = ["apps/*", "packages/*"]`.
3. In the bot, delete its `models.py`, add `autochannel-db = { workspace = true }`, and
   import `from autochannel_db import Guild, Category, Channel`.
4. Run migrations from one place only (the shared package), not from either service.
