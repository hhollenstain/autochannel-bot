# Merge autochannel-ui into autochannel-bot as a monorepo with one shared schema package

## Problem
The bot (`autochannel/data/models.py`, whose docstring says it is "shared with the auto-chan.io dashboard") and the separate `autochannel-ui` repo each keep their own copy of the `Guild`, `Category` and `Channel` SQLAlchemy models. Any schema change has to be made by hand in both repos, so the two drift apart. Moving the UI into this repo and putting the models in one package that both apps import removes the duplicate and keeps the schema in sync.

## Requirements
- R1: The repo root is a uv workspace with three members: the shared models package, the bot package (`autochannel`), and the UI. `uv sync --dev` at the root installs all three, and there is a single `uv.lock` at the root.
- R2: A new shared package (working name `autochannel_models`) is the only place in the repo that defines `Base`, `db`, `Guild`, `Category` and `Channel`. It keeps today's tables, columns, types, defaults, relationships and helper methods (`get_channels`, `get_chan_suffix`, `save_with_transaction`, `get_categories`) exactly as they are in `autochannel/data/models.py`.
- R3: The bot (`autochannel/lib/plugins/autochannels.py`, `autochannel/lib/maintenance.py`, `tests/`) imports its models from the shared package, and `autochannel/data/models.py` no longer defines any model classes.
- R4: The `autochannel-ui` source lives in a UI directory in this repo. Its own model or table definitions are deleted, and it imports `Guild`, `Category`, `Channel` and `db` from the shared package.
- R5: The bot still behaves the same. The `autochannel` console script, the `Dockerfile` bot image (`CMD ["autochannel"]`), `make test` and the existing tests all work without changes to their behaviour. The UI gets its own container build from the repo root that includes the shared package.
- R6: `.github/workflows/ci.yml` runs ruff format check, ruff check, `mypy --strict` and pytest on Python 3.13 and 3.14 for the shared package and the bot. It also runs the UI's lint and tests, so a change to the shared models runs the checks for both apps.
- R7: A regression test pins the schema: it checks that the shared `Base.metadata` contains exactly the `guild`, `category` and `channel` tables with their current columns. It also checks that the bot and the UI both resolve to that same metadata object.
- R8: `AGENTS.md` (Project Structure, Application Architecture, Getting Started) and `README.md` describe the monorepo layout. The version is bumped in `autochannel/__init__.py` (`VERSION_INFO` and `VERSION`) and `pyproject.toml`.

## Acceptance criteria
- [ ] Running `uv sync --dev` in a fresh clone exits 0. `uv run python -c "import autochannel_models, autochannel"` exits 0, and so does the equivalent import of the UI package. (R1)
- [ ] Running `grep -rnE "class (Guild|Category|Channel)\(" --include=*.py .` (excluding `.venv`) matches only files in the shared package. (R2, R3, R4)
- [ ] Running `grep -rn "__tablename__" --include=*.py .` (excluding `.venv`) matches only files in the shared package. (R2, R4)
- [ ] The existing `tests/test_models.py` and `tests/test_maintenance.py` pass, importing from the shared package, with no changes to their assertions. (R2, R3)
- [ ] Running `make test` passes, and `uv run autochannel --help` (or a start without `TOKEN`) behaves as it does on `master`. (R5)
- [ ] `docker build -f Dockerfile .` succeeds and the image's default command is `autochannel`. The UI container build from the repo root also succeeds. (R5)
- [ ] A CI run on the PR shows the lint, mypy and test jobs passing for the shared package and the bot on 3.13 and 3.14, plus the UI job passing. (R6)
- [ ] The new schema test passes. If a column is added to `Category` only in a local copy, the test fails. (R7)
- [ ] `AGENTS.md` lists the new directories, and `autochannel/__init__.py` and `pyproject.toml` show the same bumped version. (R8)

## Out of scope
- Any schema change, such as new columns, tables or migrations. This change only moves the existing models.
- Adding Alembic or any other migration tool.
- New UI features, a UI redesign, or changes to UI routes or behaviour beyond swapping its model imports.
- Changing the bot's channel maintenance logic (`queue_loop`, `lib/maintenance.py` rules).
- Changing deployment targets, image registries or `docker-compose*.yml` beyond what the new Dockerfile paths require.
- Archiving or deleting the `autochannel-ui` GitHub repo.

## Open questions
- **Access to the UI repo:** the builder needs the `autochannel-ui` source. Which repo URL and branch should it use? Should its git history be kept (for example with `git subtree add` or a merge with `--allow-unrelated-histories`), or is a plain copy acceptable?
- **Directory layout:** should the bot stay at the repo root (`autochannel/`, `tests/`, root `pyproject.toml` as a workspace member)? Or should it move to `apps/bot/`, next to `apps/ui/` and `packages/autochannel-models/`? Keeping it at the root is less disruptive to `Dockerfile`, `Makefile` and CI.
- **Shared package name and versioning:** is `autochannel_models` the right name? Should it have its own version, or follow the bot's version?
- **Schema differences:** if the UI's copy of the models differs from the bot's (extra columns, different defaults or lengths), which one is correct? This spec assumes the bot's current `models.py` is the source of truth.
- **UI stack and Python version:** the UI is assumed to be a Python/Flask app, since the models use `flask_sqlalchemy`. Does it already run on Python 3.13 or later, and should it be held to the same `ruff` and `mypy --strict` rules as the bot?
- **Removing `setup.py`:** `setup.py` duplicates the dependency list in `pyproject.toml`. Should it be removed as part of the workspace move, or left alone?
