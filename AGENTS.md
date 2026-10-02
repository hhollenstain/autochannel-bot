# AutoChannel Bot - Development Guidelines & AGENT Rules

## Project Overview
This repository contains the source code for the AutoChannel Discord bot. The bot manages automatic voice channel creation and provides various Discord bot features including:
- Automatic voice channel creation in designated categories
- Member join date tracking via context menus and slash commands
- Prometheus metrics for monitoring
- Multi-shard support for scaling

## Project Information
- **Python Version**: 3.13 (required >=3.12)
- **Dependencies**: See `pyproject.toml`
- **Main Framework**: discord.py>=2.4.0,<3.0.0
- **Build System**: setuptools with pyproject.toml
- **Package Manager**: uv (preferred) or pip

## Code Style & Requirements
- **PEP 8 Conventions**: All code must follow PEP 8 style guidelines
- **Linting & Formatting**: Use `ruff` exclusively for both formatting and checking
- **Type Hints**: Required for ALL functions and methods
- **Postponed Annotations**: Use `from __future__ import annotations` at the top of EVERY file
- **Modern Python**: Use type unions with `|` instead of `Union[X, Y]`
- **Docstrings**: Use Google-style or reStructuredText format for all public functions/classes

## Project Structure
```
autochannel/
├── __init__.py          # Package metadata and version info
├── autochannel.py       # Custom Bot class extension
├── autochannel_bot.py   # Main entrypoint and CLI
├── data/
│   ├── __init__.py
│   ├── database.py      # Database connection manager
│   └── models.py        # SQLAlchemy database models
└── lib/
    ├── __init__.py
    ├── metrics.py       # Prometheus metrics tracking
    ├── utils.py         # Utility functions
    └── plugins/
        ├── __init__.py
        ├── autochannels.py
        ├── join.py
        └── server.py
```

## Configuration & Environment
- **Environment Variables**: Copy `example.env` to `.env`
- **Required Variables**: TOKEN, APP_ID, SQLALCHEMY_DATABASE_URI
- **Optional Variables**: DBL_TOKEN, SHARD, SHARD_COUNT, TESTING_GUILD_ID, etc.

## Version Management
- **Bump Version**: Update in BOTH `autochannel/__init__.py` AND `pyproject.toml`
- **Format**: `(MAJOR, MINOR, PATCH)` → `"MAJOR.MINOR.PATCH"`
- **VERSION_INFO**: Tuple of integers for version comparison
- **VERSION**: String representation for display

## Testing & CI/CD
### Local Development
```bash
# Install dependencies
uv sync --dev

# Run tests
make test
# or
pytest -v

# Run linting
ruff format .
ruff check .
mypy --package autochannel --strict
```

### CI/CD (GitHub Actions)
- Runs on Python 3.12 and 3.13
- Executes: lint, mypy type checking, and test suite
- Failures prevent merges to protected branches

## discord.py Migration Best Practices
- **Activities**: Use `discord.Activity(name=None, type=discord.ActivityType.playing, ...)` instead of `discord.Game`
- **Colors**: Prefer `discord.Color` over `discord.Colour` (Alias, but deprecated)
- **Async Tasks**: Use `asyncio.create_task()` instead of `self.loops.create_task()`
- **Status Updates**: Use `await client.change_presence()` with Activity objects
- **Intents**: Configure explicitly using `discord.Intents` (no longer implicit)

## AGENT INTERACTION RULES

### 1. Read the Spec First
- Always read issue bodies, comments, and linked documents
- Locate specs in the workspace before making changes
- Note explicit requirements, constraints, and acceptance criteria
- If multiple specs exist, prefer the most recent or root-level spec

### 2. Implement vs. Suggest
- **NO TEMPLATING**: This is NOT a template system, do not suggest alternatives
- **DIRECT IMPLEMENTATION**: Implement exactly what the spec requires
- **NO PLACEHOLDERS**: Do not leave stubs, TODOs, or "to be completed later"
- **NO SUGGESTIONS**: Do not offer alternatives when the work is clear

### 3. Verification & Testing
- **Verify against spec**: Each change should map to a requirement
- **Lint before commit**: Always run `ruff format . && ruff check .`
- **Test after changes**: Run the test suite for any functional changes
- **Type check**: Run mypy when modifying type annotations
- **UI changes**: Call review_ui for HTML/CSS/JS/template modifications

### 4. Git & Safety
- **Never commit on main/master/trunk**: Use feature branches only
- **Never force push**: Never rewrite published history
- **No secrets**: Never commit .env, keys, credentials, or pem files
- **No .loco files**: Never commit local workspace state

### 5. Modernization
- When touching a file, apply modern practices:
  - Add proper type annotations
  - Add docstrings to public functions/classes
  - Use modern Python syntax (type unions walrus operators, etc.)
  - Follow current linting rules
  - Remove dead code and unused imports

### 6. Error Handling
- Never return fake or generated data when real APIs/files exist
- Fail with clear, actionable error messages
- Handle edge cases appropriately
- Validate inputs at function boundaries

### 7. Commit Discipline
- Small diffs are preferred but only if fully satisfying the goal
- Do not ship scaffolding or unused code
- Each commit should be self-contained and explainable
- Use descriptive commit messages explaining the WHY

## Getting Started
1. **Clone and setup**: `git clone <repo>` then `uv sync --dev`
2. **Environment**: Copy `example.env` to `.env` and configure variables
3. **Run bot**: `autochannel --debug` or `uv run python -m autochannel.autochannel_bot`
4. **Testing**: `make test` or `pytest -v` (auto-runs `uv sync --dev`)
5. **Linting**: `ruff format . && ruff check .` (use `uv run` if not in venv)

## Common Patterns
- **Logging**: Use `logging.getLogger(__name__)` for module-specific logging
- **Async functions**: Always use `async def` with `await` for I/O operations
- **CLI**: Use `argparse` with `ArgumentDefaultsHelpFormatter`
- **Database**: Session management via `DB` class with `sqlalchemy.orm.sessionmaker`
