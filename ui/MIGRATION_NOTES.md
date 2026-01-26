# UI Migration Notes - Shared Models

## Key Change: Single Source of Truth for Models

✅ **Models are now shared between UI and bot!**

Both the UI and bot now use the **same model definitions** from `autochannel/data/models.py`.

### Structure

```
autochannel-bot/
├── autochannel/
│   └── data/
│       ├── models.py      # ← SINGLE SOURCE OF TRUTH for models
│       └── database.py    # Bot's database utilities
├── ui/
│   └── autochannel/
│       └── ui/
│           └── __init__.py  # UI uses shared models from autochannel.data.models
```

### How It Works

1. **Models defined once** in `autochannel/data/models.py` (Flask-SQLAlchemy)
2. **Bot uses** models via `autochannel.data.models`
3. **UI uses** models via `autochannel.data.models` (imported in `__init__.py`)
4. **Both share** the same `db` instance from `autochannel.data`

### Import Pattern

**In UI code, import models like this:**

```python
# ✅ Correct - Use shared models
from autochannel.data import db
from autochannel.data.models import Guild, Category, Channel

# ❌ Wrong - Don't import from autochannel.ui.models (doesn't exist)
from autochannel.ui.models import Guild  # This won't work!
```

### Benefits

1. **No duplication** - Models defined once, used by both
2. **Synchronized** - Changes to models affect both UI and bot
3. **Consistent** - Same table definitions, relationships, and methods
4. **Simpler** - No need to keep two model files in sync

### Migration Checklist

When copying UI files, update imports:

- [ ] `from autochannel.models` → `from autochannel.data.models`
- [ ] `from autochannel import db` → `from autochannel.data import db`
- [ ] `autochannel.api.*` → `autochannel.ui.api.*` (UI-specific code only)
- [ ] `autochannel.site.*` → `autochannel.ui.site.*` (UI-specific code only)
- [ ] `autochannel.errors.*` → `autochannel.ui.errors.*` (UI-specific code only)
- [ ] `autochannel.lib.*` → `autochannel.ui.lib.*` (UI-specific code only)
- [ ] `autochannel.config` → `autochannel.ui.config` (UI-specific code only)

### Example Updates

**Before (old UI repo):**
```python
from autochannel import db
from autochannel.models import Guild, Category, Channel
```

**After (unified repo):**
```python
from autochannel.data import db
from autochannel.data.models import Guild, Category, Channel
```

---

*Models are shared - no duplication needed!*
