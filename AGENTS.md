# AutoChannel Bot - Development Guidelines

## Project Overview
This repository contains the source code for the AutoChannel Discord bot. The bot manages automatic voice channel creation and provides various Discord bot features including:
- Automatic voice channel creation in designated categories
- Member join date tracking via context menus and slash commands
- Prometheus metrics for monitoring
- Multi-shard support for scaling

## Code Style
- Code follows PEP 8 conventions
- Use of `ruff` for linting and formatting
- Type hints are required for all functions
- Use `from __future__ import annotations` at the top of each file to enable postponed evaluation of annotations

## Project Structure
- `autochannel/` - Core bot code
  - `__init__.py` - Package metadata and version info
  - `autochannel.py` - Custom Bot class implementation
  - `autochannel_bot.py` - Main entrypoint
  - `data/` - Database models and session management
  - `lib/` - Utility functions and plugins
    - `plugins/` - Discord cog extensions
    - `metrics.py` - Prometheus metrics tracking
    - `utils.py` - Helper functions
- `.github/workflows/` - GitHub Actions CI/CD pipelines
- `ruff.toml` - Ruff linter configuration

## Version Management
- Bump version in both `autochannel/__init__.py` (VERSION_INFO and VERSION) and `pyproject.toml` when shipping changes
- Format: `(MAJOR, MINOR, PATCH)` → `"MAJOR.MINOR.PATCH"`

## Testing & Linting
- **Linting**: `ruff format . && ruff check .`
- **Type checking**: `mypy --package autochannel --strict`
- **Testing**: `make test` or `pytest -v`
- CI runs lint, type check, and tests on Python 3.10, 3.11, 3.12

## Discord.py Migration Notes
- `discord.Game` → `discord.Activity(type=discord.ActivityType.playing)`
- `discord.Colour` → `discord.Color` (alias, but Color is recommended)
- `self.loops.create_task()` → `asyncio.create_task()`

## AGENT INTERACTION GUIDELINES
1. **Read the spec first**: Always check issue bodies, comments, and linked documents before making changes
2. **Verify against spec**: Each change should map to a requirement in the spec
3. **Don't leave stubs**: Complete the work in this run when possible
4. **Modernize when updating**: When touching a file, apply modern practices (type hints, proper error handling, etc.)
5. **Lint before commit**: Run `ruff format . && ruff check .` before staging changes
6. **Test after changes**: Always run the test suite after functional changes

## Getting Started
1. Install dependencies: `uv sync --dev`
2. Set up environment: Copy `example.env` to `.env` and configure
3. Run bot: `autochannel --debug` or `uv run python -m autochannel.autochannel_bot`
4. Run tests: `make test` or `pytest -v` (ensures `uv sync --dev` is run first)
5. Check lint: `ruff format . && ruff check .` (use `uv run` if not in venv)
