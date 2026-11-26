# AutoChannel

Monorepo for the AutoChannel Discord bot and its auto-chan.io dashboard. Both services
read and write the same Postgres database, so they share one schema package and are
built, tested and released together.

| Path | What it is |
| :--- | :--------- |
| [`apps/bot/`](apps/bot/) | The Discord bot (`autochannel` package, `autochannel` console script) |
| [`apps/ui/`](apps/ui/) | The dashboard: Flask API (`autochannel_ui`) + React SPA (`frontend/`) |
| [`packages/autochannel-db/`](packages/autochannel-db/) | Shared SQLAlchemy models + Alembic migrations (`autochannel_db`) |

## Development

Requires Python 3.14, [uv](https://docs.astral.sh/uv/), and Node 24 for the UI frontend.

```sh
make install       # uv sync --all-packages + npm ci
make test          # bot and UI checks
make build-images  # both Docker images, built from the repo root
make migrate       # alembic upgrade head against $SQLALCHEMY_DATABASE_URI
```

The root `pyproject.toml` is a virtual [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
with a single `uv.lock`, so both apps always resolve the same `autochannel-db` and
SQLAlchemy versions.

## Schema changes

Change the models only in `packages/autochannel-db/src/autochannel_db/models.py`, and add
an Alembic revision in the same PR:

```sh
uv run alembic -c packages/autochannel-db/alembic.ini revision --autogenerate -m "..."
```

## Releasing and deploying

The bot and the dashboard are released **together**. Publishing a GitHub Release runs
`.github/workflows/release.yml`, which:

1. Builds both images from the release commit and pushes `autochannel-bot:<tag>` and
   `autochannel-ui:<tag>` (GHCR, plus Docker Hub when `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN`
   are set).
2. Only after both succeed, moves `:latest` on both images to those digests.

Deploy both from the same tag with the root `docker-compose.yml`:

```sh
AUTOCHANNEL_TAG=<tag> docker compose up -d
```

Its `migrate` service runs `alembic upgrade head` from that tag first. `bot` and `ui` start
only after it succeeds, so neither app runs against an older schema than its models.
