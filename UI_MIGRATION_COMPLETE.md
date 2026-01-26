# UI Migration - Completion Summary

## Status

✅ **Infrastructure Ready** - Dockerfiles, configs, and structure created
⏳ **Files Need Copying** - UI source files need to be copied from `autochannel-ui` repo

## Completed Setup

### 1. Directory Structure ✅
- `ui/autochannel/ui/` - Created for UI application code
- `ui/Dockerfile` - Multi-stage UV-based Dockerfile created
- `ui/pyproject.toml` - UV package configuration created
- `ui/MIGRATION_STEPS.md` - Detailed migration instructions

### 2. Docker Configuration ✅
- `ui/Dockerfile` - Separate Docker image for UI
- `docker-compose.yml` - Updated with both `bot` and `ui` services
- `.dockerignore` - Updated to exclude UI build artifacts from bot builds

### 3. Package Structure ✅
- `ui/autochannel/__init__.py` - Package init created
- `ui/autochannel/ui/__init__.py` - Flask app factory created
- `ui/autochannel/ui/models.py` - Model definitions (same as bot, bound to Flask-SQLAlchemy)

### 4. Model Integration ✅
- UI models match bot models (same table definitions)
- UI uses Flask-SQLAlchemy (required for Flask)
- Bot uses Flask-SQLAlchemy (compatible)
- Both point to the same database
- Both use shared migrations

## Next Steps: Copy UI Files

Run these commands to complete the migration:

```bash
cd /Users/henryhollenstain/projects/autochannel-bot

# Copy UI application code
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/api ui/autochannel/ui/
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/site ui/autochannel/ui/
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/errors ui/autochannel/ui/
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/lib ui/autochannel/ui/
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/data ui/autochannel/ui/

# Copy static files and templates
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/static ui/autochannel/ui/
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/templates ui/autochannel/ui/

# Copy configuration and entry points
cp /Users/henryhollenstain/projects/autochannel-ui/autochannel/config.py ui/autochannel/ui/
cp /Users/henryhollenstain/projects/autochannel-ui/autochannel/views.py ui/autochannel/ui/
cp /Users/henryhollenstain/projects/autochannel-ui/autochannel/forms.py ui/autochannel/ui/
cp /Users/henryhollenstain/projects/autochannel-ui/run.py ui/
cp /Users/henryhollenstain/projects/autochannel-ui/manage.py ui/
```

## Import Updates Required

After copying files, update these imports to use **shared models**:

### In `ui/autochannel/ui/data/data_functions.py`:
```python
# Change from:
from autochannel import db
from autochannel.models import Guild, Category, Channel

# To (use shared models from bot):
from autochannel.data import db
from autochannel.data.models import Guild, Category, Channel
```

### In `ui/autochannel/ui/data/data_forms.py`:
```python
# Change from:
from autochannel import db
from autochannel.models import Guild, Category

# To (use shared models from bot):
from autochannel.data import db
from autochannel.data.models import Guild, Category
```

### In all other UI files with model imports:
```python
# Change from:
from autochannel import db
from autochannel.models import Guild, Category, Channel

# To (use shared models):
from autochannel.data import db
from autochannel.data.models import Guild, Category, Channel
```

### In `ui/autochannel/ui/site/routes.py`, `api/routes.py`, etc.:
```python
# Change from:
from autochannel import db
from autochannel.models import Guild, Category

# To:
from autochannel.data import db
from autochannel.data.models import Guild, Category
```

### In `ui/autochannel/ui/lib/decorators.py`:
```python
# Change from:
from autochannel import db
from autochannel.models import Guild, Category

# To:
from autochannel.data import db
from autochannel.data.models import Guild, Category
```

### For UI-specific code (no model imports):
- `autochannel.api.*` → `autochannel.ui.api.*`
- `autochannel.site.*` → `autochannel.ui.site.*`
- `autochannel.errors.*` → `autochannel.ui.errors.*`
- `autochannel.lib.*` → `autochannel.ui.lib.*`
- `autochannel.config` → `autochannel.ui.config`

### In `ui/run.py`:
```python
# Change from:
from autochannel.lib import utils
from autochannel import create_app

# To:
from autochannel.ui.lib import utils
from autochannel.ui import create_app
```

**Important:** Models are now shared! Both UI and bot use `autochannel.data.models` - no duplicate model definitions.

## Testing

After migration:

```bash
# Build UI image
docker build -f ui/Dockerfile -t autochannel-ui:test .

# Build bot image
docker build -f Dockerfile -t autochannel-bot:test .

# Run both services
docker-compose up --build
```

## Structure Overview

```
autochannel-bot/
├── autochannel/              # Bot code
│   └── data/
│       └── models.py         # Bot models (Flask-SQLAlchemy)
├── ui/                       # UI code
│   ├── autochannel/
│   │   └── ui/              # UI application
│   │       ├── models.py    # UI models (Flask-SQLAlchemy, same schema)
│   │       ├── api/         # API routes
│   │       ├── site/        # Site routes
│   │       ├── errors/      # Error handlers
│   │       ├── lib/         # Utilities
│   │       ├── data/        # Data functions
│   │       ├── static/      # Static files
│   │       └── templates/   # HTML templates
│   ├── Dockerfile           # UI Dockerfile
│   ├── pyproject.toml       # UI package config
│   └── run.py              # UI entry point
├── migrations/              # Shared migrations
└── docker-compose.yml       # Both services
```

## Notes

- Both UI and bot models use Flask-SQLAlchemy (compatible)
- Both use the same database (SQLALCHEMY_DATABASE_URI)
- Both use the same migrations directory
- Models have identical table definitions
- Each service has its own Dockerfile and image
- Docker Compose orchestrates both services

---

*Migration setup completed. Copy files to complete migration.*
