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
    - `__init__.py`
    - `database.py`
    - `models.py`
  - `lib/` - Utility functions and plugins
    - `plugins/` - Discord cog extensions
    - `metrics.py` - Prometheus metrics tracking
    - `utils.py` - Helper functions
- `.github/workflows/` - GitHub Actions CI/CD pipelines
- `ruff.toml` - Ruff linter configuration

## Application Architecture
The AutoChannel bot follows a modular architecture with the following component relationships:
1. **Main Entry Point**: `autochannel_bot.py` initializes the bot and sets up configuration
2. **Core Bot Class**: `autochannel.py` extends discord.Client with custom functionality 
3. **Database Layer**: `data/` package handles all database interactions via SQLAlchemy
4. **Plugin System**: `lib/plugins/` contains Discord cogs that extend bot functionality
5. **Metrics**: `lib/metrics.py` provides Prometheus monitoring integration
6. **Utility Functions**: `lib/utils.py` contains shared helper functions

The bot initialization flow:
1. `autochannel_bot.main()` is called from CLI entry point
2. Configuration is loaded from `.env` file
3. Database connection is established via `data/database.py`
4. All cogs in `lib/plugins/` are registered with the bot instance
5. The bot connects to Discord using the provided token

## Key Dependencies
- **discord.py**: >=2.4.1 - Primary framework for interacting with Discord API
- **SQLAlchemy**: Database ORM for PostgreSQL integration
- **aiohttp**: Asynchronous HTTP client for API requests
- **Flask-SQLAlchemy**: Integration between Flask and SQLAlchemy for database management

### discord.py Documentation
The AutoChannel bot uses [discord.py](https://discordpy.readthedocs.io/) as its primary framework. This library provides:
- Asynchronous interaction with the Discord API using `async`/`await`
- Object-oriented design that maps Discord concepts directly to Python objects  
- Built-in rate limit handling to prevent 429 errors
- Command extension system for creating bot commands
- Support for voice channels, guild management, and user interactions

The documentation for discord.py can be found at: [https://discordpy.readthedocs.io/](https://discordpy.readthedocs.io/)
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

## How to Use
The AutoChannel bot can be run using several entry points:

### Primary Entry Points

1. **Command Line Interface (CLI):**
   ```bash
   autochannel --debug
   ```
   This is the recommended way to start the bot, as it automatically:
   - Reads configuration from `.env`
   - Initializes all required components
   - Starts the main Discord event loop
   - Handles graceful shutdown signals

2. **Python Module Execution:**
   ```bash
   uv run python -m autochannel.autochannel_bot
   ```
   This directly executes the main bot module which:
   - Sets up logging and configuration
   - Initializes the database connection
   - Registers all commands and cogs
   - Connects to Discord via the provided token

3. **Direct Module Import:**
   ```python
   from autochannel.autochannel_bot import main

   main()
   ```
   This approach is useful for integration testing or running in containerized environments where you may need to customize startup behavior.

### Configuration
The bot requires a `.env` file with:
- `DISCORD_TOKEN`: Your Discord bot token
- Database connection settings (POSTGRES_URL)
- Other environment variables as needed

For development, copy `example.env` to `.env` and update the values.
