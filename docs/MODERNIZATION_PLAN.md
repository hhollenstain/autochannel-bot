# AutoChannel Modernization Plan

This document captures the plan to modernize the `autochannel-bot` and `autochannel-ui` projects, consolidate them into a single monorepo, refresh dependencies, and rebuild the UI with a modern frontend stack.

Each phase below maps to its own branch and PR so review is incremental and revertible.

---

## Phase 1 — Code cleanup & bug fixes (PR 1)

**Branch:** `chore/code-cleanup`

**Goal:** Fix latent bugs, dead code, and code-smell hotspots without changing dependencies or architecture. This makes every later PR safer.

### Bot (`autochannel-bot`)

Real bugs:
- `autochannel/lib/plugins/autochannels.py::on_vc_error` — references undefined `ctx` and `self.cat_names(ctx)` (method does not exist), and concatenates a string into `error` (a `CommandError`/`AppCommandError` object). Will raise inside the error handler.
- `autochannel/lib/plugins/autochannels.py` — `from unicodedata import category` shadows the local `category` parameter used throughout the cog.
- `autochannel/lib/plugins/autochannels.py::AutoChannels.__init__` schedules tasks on `self.autochannel.loop` from `__init__`. In modern discord.py the loop isn't guaranteed to exist there; move scheduling into `cog_load` / `setup_hook`.
- `autochannel/lib/plugins/server.py::on_command_error` — `msg` may be referenced unbound when none of the `isinstance` branches match before the final check; and the cog is registered with `commands.Cog.listener()` missing — it relies on the implicit method name pattern but since this is a Cog the listener decorator is needed to actually wire it up.
- `autochannel/data/database.py` opens a new SQLAlchemy `Session` once per bot startup and stores it on `self.session` for the **lifetime** of the process. Long-lived sessions accumulate stale state and the explicit `session.expire_all()` calls in the autochannels plugin are a workaround. We'll switch to a `sessionmaker` and acquire short-lived sessions per task.
- `autochannel/data/models.py` imports `flask_sqlalchemy` — the bot has no Flask app, no app context, and only "works" because `db.Model` registers a metadata at import time. The bot should use plain SQLAlchemy 2.x ORM (`DeclarativeBase`).
- `autochannel/lib/plugins/autochannels.py:559` uses `before.channel.category_id` (works) but more idiomatic and safer is `before.channel.category`.
- `setup.py` lists: `dblpy` twice, `asyncio` (stdlib — should never be a dep), `pip` (should never be a dep), `aiomeasures` (unused), `flask_sqlalchemy` (the bot doesn't need Flask), and an unused `dblpy` import path that's known broken (`ac_dbl.py` is already commented out in the extension list).
- `autochannel/lib/plugins/ac_dbl.py` uses `dbl` (`dblpy`) which is unmaintained and incompatible with modern discord.py. Either drop it or migrate to `topggpy`. **Recommend dropping** until/unless top.gg integration is reintroduced.
- Missing `__init__.py` for `autochannel/data/`. It's been working only because of namespace package fallback.

Cleanup:
- Strip auto-generated `[summary]`/`[type]` placeholder docstrings throughout (low-signal noise) — keep only docstrings that say something real.
- Remove dead/commented imports.
- Replace bare `except:` with `except Exception:` and log.
- Add basic linting/formatting config (`ruff` for lint+format) so subsequent PRs are mechanical.

### UI (`autochannel-ui`)

Real bugs (most important first):
- **Auth bypass on multiple routes.** Decorator order is wrong on at least:
  - `api/routes.py::add_guild` — `@login_required` above `@mod_api.route(...)`
  - `site/routes.py::dashboard_index` — same pattern
  - `site/routes.py::add_guild` — same pattern
  Flask's `@blueprint.route` registers the **inner** function as the URL handler and returns the inner function unchanged. With `@login_required` placed above `@route`, the wrapped function is never registered — the route is **public**. Fix is to put `@route` outermost (above `@login_required`).
- `errors/routes.py::_handle_api_error` references `request` and `jsonify_error` that aren't imported. Will `NameError` if invoked.
- `autochannel/site/routes.py::dashboard_guild` — `discord_categories` may be `None` (silently falls through); the existing `else` for the invite redirect is fine but the API path also returns `None` on non-200, which we should propagate as a flash + retry.
- `autochannel/api/routes.py::callback` uses `itsdangerous.JSONWebSignatureSerializer` which was **removed in itsdangerous 2.1+**. The pin `itsdangerous<2.1` in `setup.py` confirms this. We'll switch to `itsdangerous.URLSafeSerializer` or, better, drop the home-rolled "api_key" entirely (the user_id is already in the session — no JWS needed).

Cleanup:
- Delete empty stub files: `autochannel/forms.py`, `autochannel/views.py`.
- Delete duplicate templates: `autochannel/templates/includes/footer copy.html`.
- Delete checked-in dev artifacts: `autochannel/site.db`, `AutoChannel_ui.egg-info/`.
- Remove `test-db.py` (one-off script with hardcoded prod IDs).
- Remove `db_create.py` in favor of Alembic-only flow.
- Strip `[summary]` placeholder docstrings.

### Acceptance for PR 1

- [ ] Existing bot starts and `/sync` works against a test guild.
- [ ] Existing UI serves `/`, login flow, and dashboard with no regressions.
- [ ] No new dependencies introduced.
- [ ] `ruff check` passes on both packages.

---

## Phase 2 — Upgrade discord.py and Python (PR 2)

**Branch:** `feat/discord-py-upgrade`

**Goal:** Move from `discord.py==2.3.2` (Python 3.10) to the latest `discord.py 2.5.x`, on Python 3.12. Fix the API drift this entails.

### Concrete changes

- `python_requires = ">=3.12"`. Update `Dockerfile` from `python:3.10-alpine` → `python:3.12-slim` (Alpine + Python wheels is a known pain; `slim` is faster to build and supports binary wheels for psycopg/aiohttp).
- `discord.py==2.5.*` (will pin to a specific minor).
- API audit:
  - `bot.loop.create_task(...)` from `__init__` → schedule from `setup_hook` / `cog_load`.
  - Confirm `Intents` declarations are explicit (`message_content` if needed; for a slash-command-only bot we should drop `message_content`).
  - Audit `app_commands.AppCommandError` handlers — signatures are stable but error class hierarchy changed slightly between 2.3 and 2.5.
  - Confirm `interaction.response.send_message` vs `followup` usage — long-running DB ops should defer.
- Replace `profanityfilter` (unmaintained, last release 2018) with `better-profanity` (still maintained). Optional; can also be deferred behind a feature flag and only run when `custom_enabled`.
- Replace `dblpy` (or remove the cog entirely, see Phase 1).
- Refresh `prometheus_client`, `coloredlogs`, `psycopg` (move from `psycopg2-binary` → `psycopg[binary]` v3 — async-friendly).

### Acceptance for PR 2

- [ ] Bot starts on Python 3.12 with discord.py 2.5.x.
- [ ] All slash commands sync to a test guild.
- [ ] Voice state events still trigger create/delete.
- [ ] Prometheus endpoint returns metrics on `:8000/metrics`.

> Note: **Phase 2 is intentionally before the monorepo migration**. Doing the upgrade first means the migration in Phase 3 carries already-modernized code and we don't conflate "moved files" with "behavioral changes" in one PR.

---

## Phase 3 — Monorepo consolidation (PR 3)

**Branch:** `feat/monorepo`

**Goal:** Merge `autochannel-bot` and `autochannel-ui` into a single repo with a shared `core` package that owns the data model and migrations. This is what fixes the "maintaining the same models in two places" pain.

### Proposed layout

```
autochannel/                      (new repo, or reuse autochannel-bot renamed)
├── pyproject.toml                # workspace root, declares uv workspace
├── uv.lock
├── README.md
├── Makefile                      # convenience commands
├── docker-compose.yml            # local dev: postgres, bot, ui
├── docker-compose.dev.yml        # overrides for hot-reload
├── docker-compose.exporters.yml  # optional metrics stack
├── .github/workflows/            # CI per package
│   ├── ci-core.yml
│   ├── ci-bot.yml
│   └── ci-ui.yml
├── packages/
│   ├── core/                     # shared: models, migrations, config
│   │   ├── pyproject.toml
│   │   ├── src/autochannel_core/
│   │   │   ├── __init__.py
│   │   │   ├── models.py         # SQLAlchemy 2.x DeclarativeBase
│   │   │   ├── db.py             # engine + sessionmaker factories
│   │   │   ├── settings.py       # pydantic-settings, env-driven
│   │   │   └── migrations/       # alembic single source of truth
│   │   └── tests/
│   ├── bot/                      # discord bot
│   │   ├── pyproject.toml        # depends on autochannel-core
│   │   ├── Dockerfile
│   │   ├── src/autochannel_bot/
│   │   │   ├── __init__.py
│   │   │   ├── bot.py            # AutoChannel client
│   │   │   ├── main.py           # entrypoint
│   │   │   └── cogs/
│   │   │       ├── autochannels.py
│   │   │       ├── server.py
│   │   │       └── join.py
│   │   └── tests/
│   └── ui/                       # web app (see Phase 4 for stack)
│       ├── pyproject.toml        # depends on autochannel-core
│       ├── Dockerfile
│       ├── src/autochannel_ui/   # backend
│       └── frontend/             # SPA (added in Phase 4)
└── tools/                        # one-off scripts, db helpers
```

### Migration procedure

We'll preserve git history from both repos using `git subtree` or `git-filter-repo --to-subdirectory-filter`:

1. Create new `autochannel` repo (or rename `autochannel-bot` → `autochannel`).
2. `git filter-repo --to-subdirectory-filter packages/bot` on a clone of bot.
3. `git filter-repo --to-subdirectory-filter packages/ui` on a clone of ui.
4. Merge both filtered histories into the monorepo with `git merge --allow-unrelated-histories`.
5. Extract `models.py` + Alembic migrations into `packages/core` and update both bot and ui to import from `autochannel_core`.
6. Adopt **`uv` workspaces** (`[tool.uv.workspace]`) — single `uv.lock`, fast installs, works in CI and Docker.
7. Replace `Pipfile` / `setup.py` with a `pyproject.toml` per package.
8. Single Alembic config in `packages/core/src/autochannel_core/migrations` — both services run `alembic upgrade head` on boot or via `make migrate`.

### Acceptance for PR 3

- [ ] `uv sync` from repo root installs both services.
- [ ] `uv run autochannel-bot` and `uv run autochannel-ui` start locally.
- [ ] Bot & UI both import `Guild`, `Category`, `Channel` from `autochannel_core.models`.
- [ ] `alembic upgrade head` works against a fresh Postgres and the existing prod DB.
- [ ] CI has separate jobs per package; `core` is tested first, `bot` and `ui` test in parallel.
- [ ] Old repos are archived (read-only) after the cutover with a redirect note in their README.

---

## Phase 4 — Modern frontend (split into 4a + 4b)

**Branches:** `feat/ui-backend-fastapi` (4a), `feat/ui-frontend-spa` (4b)

**Goal:** Replace the Flask+Jinja+jQuery+Bootstrap-Toggle UI with a FastAPI backend and a Vite/React SPA.

> TipTap was originally on the table but isn't needed — the dashboard has no rich-content authoring surfaces. The modernization value comes from the stack itself: type-safety, mobile-responsive components, no jQuery, no Bootstrap-Toggle, no `flask_*` legacy.

### 4a — Backend (`feat/ui-backend-fastapi`)

- `packages/ui/src/autochannel_ui/` becomes a FastAPI app exposing JSON endpoints that mirror the current `mod_api` blueprint:
  - `GET  /api/me` — current user + managed guilds (cached).
  - `GET  /api/guilds/{guild_id}/categories` — DB + Discord category data.
  - `PATCH /api/guilds/{guild_id}/categories/{category_id}` — single endpoint for `enabled`, `prefix`, `channel_size`, `empty_count`, `custom_enabled`, `custom_prefix` (replaces the 6 separate POST endpoints).
  - `POST /api/guilds/{guild_id}/install` — replaces `/api/add-guild`.
  - `GET  /auth/login`, `/auth/callback`, `/auth/logout` — OAuth2 via `Authlib`.
- Reuses `autochannel_core` for ORM. Uses async SQLAlchemy with `psycopg[async]`.
- Pydantic v2 schemas for request/response — same models the React client will type against.
- Server-side session via `starsessions` (signed cookie) — drops the `JSONWebSignatureSerializer` workaround entirely.
- Prometheus metrics via `prometheus-fastapi-instrumentator`.
- Replaces: `flask_bootstrap`, `flask_script`, `flask_debugtoolbar`, `flask_compress`, `flask_bcrypt`, `flask_sqlalchemy`, `wtforms`, `wtforms-alchemy`, `requests` (→ `httpx`).

### 4b — Frontend (`feat/ui-frontend-spa`)

- `packages/ui/frontend/` — Vite + React + TypeScript.
- TanStack Query for data fetching/caching, TanStack Router for routing.
- shadcn/ui (Radix + Tailwind) for the component layer; replaces every Bootstrap 4 widget and the bootstrap-toggle dependency.
- `react-hook-form` + `zod` for form state (the current per-row inline-edit pattern becomes typed).
- Sonner (toasts) replaces `toastr.js`.
- OpenAPI types auto-generated from FastAPI's `/openapi.json` so the client is type-safe end-to-end.

### Hosting

- Single container per service (matches existing DigitalOcean deployment): the FastAPI image runs `uvicorn` and serves the built SPA from `/` and the API at `/api/*`. Vite handles asset hashing; `Cache-Control: immutable` for hashed bundles.

### Acceptance for PR 4 (a + b)

- [ ] Feature parity with the current dashboard:
  - List managed guilds → enter a guild → toggle enable, edit prefix, channel size, empty count, custom enable, custom prefix.
  - Discord OAuth login + logout.
  - 404 page.
- [ ] Mobile-responsive.
- [ ] Lighthouse > 90 on Performance, Accessibility, Best Practices.
- [ ] No jQuery, no Bootstrap-Toggle, no `flask_*` packages remaining.
- [ ] Image size compatible with current DO droplet (single Docker image, multi-stage build keeps the final layer < 250MB).

---

## Locked-in decisions

| Topic               | Decision                                                                         |
|---------------------|----------------------------------------------------------------------------------|
| Monorepo strategy   | Rename `autochannel-bot` → `autochannel`, merge `autochannel-ui` history in.     |
| Python tooling      | `uv` workspaces, single `uv.lock`, `pyproject.toml` per package.                  |
| Frontend            | FastAPI + Vite + React + TypeScript + TanStack Query + shadcn/ui. No TipTap.      |
| top.gg integration  | Restore via `topggpy` in Phase 2.                                                 |
| Deployment          | Same DigitalOcean (droplet + managed Postgres). Optimize for small image size.   |

---

## PR-by-PR summary

| # | Branch                       | Scope                                                                         | Risk    |
|---|------------------------------|-------------------------------------------------------------------------------|---------|
| 1 | `chore/code-cleanup`         | Fix bugs (incl. UI auth bypass), kill dead code, add ruff. No dep changes.    | low     |
| 2 | `feat/discord-py-upgrade`    | Python 3.12, discord.py 2.5.x, swap dblpy → topggpy, psycopg v3.              | medium  |
| 3 | `feat/monorepo`              | Combine repos, extract `core`, adopt uv workspaces + single Alembic.          | medium  |
| 4a| `feat/ui-backend-fastapi`    | FastAPI backend, async SQLAlchemy, parity with current `mod_api`/`mod_site`.  | medium  |
| 4b| `feat/ui-frontend-spa`       | Vite/React SPA, shadcn/ui, parity with current dashboard.                     | medium  |

Each PR is independently reviewable; PR 4b stacks on PR 4a since it consumes its OpenAPI schema.
