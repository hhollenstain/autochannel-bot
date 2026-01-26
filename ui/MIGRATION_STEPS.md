# UI Migration Steps

## Overview

This document provides step-by-step instructions for migrating `autochannel-ui` into the `autochannel-bot` repository.

## Directory Structure

After migration, the structure should be:

```
autochannel-bot/
├── autochannel/              # Bot code
│   └── data/
│       └── models.py         # Shared models (source of truth)
├── ui/                       # UI code (NEW)
│   ├── autochannel/
│   │   └── ui/              # UI application code
│   │       ├── api/
│   │       ├── site/
│   │       ├── errors/
│   │       ├── lib/
│   │       ├── data/
│   │       ├── static/      # CSS, JS, images
│   │       └── templates/   # HTML templates
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── run.py
├── migrations/               # Shared migrations
└── docker-compose.yml        # Both services
```

## Migration Steps

### 1. Copy UI Source Code

```bash
cd /Users/henryhollenstain/projects/autochannel-bot

# Copy UI application code
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/* ui/autochannel/ui/

# Copy static files
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/static ui/autochannel/ui/

# Copy templates
cp -r /Users/henryhollenstain/projects/autochannel-ui/autochannel/templates ui/autochannel/ui/

# Copy entry point
cp /Users/henryhollenstain/projects/autochannel-ui/run.py ui/

# Copy configuration if needed
cp /Users/henryhollenstain/projects/autochannel-ui/autochannel/config.py ui/autochannel/ui/

# Copy manage.py if needed
cp /Users/henryhollenstain/projects/autochannel-ui/manage.py ui/
```

### 2. Update Model Imports

In `ui/autochannel/ui/models.py` or wherever models are imported, change:

```python
# Old (UI repo)
from autochannel import db
from autochannel.models import Channel, Category, Guild

# New (shared models from bot)
from autochannel.data import db
from autochannel.data.models import Channel, Category, Guild
```

Or remove the models file entirely and import from bot:

```python
# In UI code, import shared models
from autochannel.data import db
from autochannel.data.models import Channel, Category, Guild
```

### 3. Update Import Paths

Update all imports in UI code to work with new structure. The UI code should import from:
- `autochannel.ui.*` for UI-specific code
- `autochannel.data.models` for shared models

### 4. Update __init__.py Files

Create `ui/autochannel/__init__.py`:
```python
"""AutoChannel UI Package"""
```

Create `ui/autochannel/ui/__init__.py` (copy from UI repo and update imports if needed):
```python
from flask import Flask
from autochannel.data import db

def create_app():
    app = Flask(__name__)
    # ... rest of app setup
    return app
```

### 5. Test Build

```bash
# Build UI Docker image
docker build -f ui/Dockerfile -t autochannel-ui:test .

# Build bot Docker image  
docker build -f Dockerfile -t autochannel-bot:test .

# Test with docker-compose
docker-compose up --build
```

### 6. Update Environment Variables

Ensure `.env` file has all required variables for both services:

```bash
# Shared
SQLALCHEMY_DATABASE_URI=postgresql://...

# Bot specific
TOKEN=...
AUTO_CATEGORIES=...

# UI specific
OAUTH2_CLIENT_ID=...
OAUTH2_CLIENT_SECRET=...
OAUTH2_REDIRECT_URI=...
FLASK_APP=run.py
FLASK_ENV=production
```

## Verification Checklist

- [ ] UI code copied to `ui/autochannel/ui/`
- [ ] Static files copied to `ui/autochannel/ui/static/`
- [ ] Templates copied to `ui/autochannel/ui/templates/`
- [ ] `run.py` copied to `ui/`
- [ ] Model imports updated to use shared models
- [ ] Dockerfiles created and tested
- [ ] `docker-compose.yml` updated with both services
- [ ] Environment variables configured
- [ ] Both services can access shared database
- [ ] Both services can access shared migrations

## Benefits

1. **Single Repository**: All code in one place
2. **Shared Models**: Single source of truth
3. **Shared Migrations**: Already consolidated
4. **Independent Images**: Still separate Docker builds
5. **Easier Development**: One repo to clone and work with

## Notes

- UI and bot remain separate Docker images
- Both use the same database
- Both use the same migration files
- Models are shared from `autochannel/data/models.py`
- Each service has its own `pyproject.toml` for dependencies
- Build contexts are different for each Dockerfile
