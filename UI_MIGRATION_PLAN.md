# UI Migration Plan

## Overview

Migrate `autochannel-ui` into `autochannel-bot` repository as a separate Docker image and service, while keeping them as independent deployable units.

## Structure

```
autochannel-bot/
├── autochannel/          # Bot code
│   └── data/
│       └── models.py     # Shared models (source of truth)
├── ui/                   # UI code (NEW)
│   ├── autochannel/
│   │   └── ui/          # UI application code
│   ├── Dockerfile       # UI Dockerfile
│   ├── pyproject.toml   # UI package config (UV)
│   └── run.py          # UI entry point
├── migrations/          # Shared migrations
├── docker-compose.yml   # Both services
└── Dockerfile           # Bot Dockerfile
```

## Migration Steps

### Phase 1: Directory Structure ✅
- Create `ui/` directory
- Create `ui/autochannel/ui/` for UI app code
- Set up directory structure

### Phase 2: Copy UI Code
- Copy UI application code
- Copy static files and templates
- Copy configuration files
- Update imports to reference shared models

### Phase 3: Docker & Build
- Create `ui/Dockerfile` for UI
- Create `ui/pyproject.toml` (UV-based)
- Update root `docker-compose.yml` for both services
- Update `.dockerignore`

### Phase 4: Model Integration
- UI uses `autochannel.data.models` (shared)
- Remove duplicate model files from UI
- Ensure both reference same models

### Phase 5: Testing & Validation
- Test UI builds separately
- Test both services together
- Verify shared database works

## Benefits

1. **Single Repository**: Both services in one repo
2. **Shared Migrations**: Already consolidated
3. **Shared Models**: Single source of truth
4. **Independent Deployments**: Still separate Docker images
5. **Simplified Development**: One repo to manage

## Notes

- UI will be in `ui/` directory
- Bot remains in `autochannel/` directory
- Both use shared `migrations/`
- Both use shared `autochannel/data/models.py`
- Each has its own Dockerfile
- Docker Compose orchestrates both
