# Why `ModuleNotFoundError: No module named 'autochannel.ui'` Keeps Happening

## The Core Problem

The error persists because **Python cannot find the `autochannel.ui` module** at runtime, even though:
1. The UI package is being built and installed
2. The source is being copied to `/app/autochannel/ui`
3. `PYTHONPATH` includes `/app`

## Root Cause Analysis

### 1. **Package Installation Path Mismatch**

The UI package's `pyproject.toml` specifies:
```toml
[tool.hatch.build.targets.wheel]
packages = ["autochannel/ui"]
```

**What this means:**
- Hatchling looks for `autochannel/ui` **relative to where `pyproject.toml` is located**
- Since `pyproject.toml` is in `./ui/`, hatchling looks for `./ui/autochannel/ui`
- When installed, it creates `autochannel/ui` in site-packages

**The problem:**
- When Python tries to import `autochannel.ui`, it needs:
  - `autochannel/__init__.py` (from bot package) ✅
  - `autochannel/ui/__init__.py` (from UI package) ❓
- If the UI package doesn't install correctly, or if the structure in site-packages is wrong, Python can't find it

### 2. **Source Copy Timing Issue**

In the Dockerfile:
```dockerfile
COPY --from=builder /app/ui/autochannel/ui /app/autochannel/ui
```

**The problem:**
- This copy happens **after** the bot's `autochannel` package is copied
- But if the copy fails silently or the path doesn't exist in the builder, the UI source won't be in `/app`
- Even if it exists, Python might not find it if the structure is wrong

### 3. **PYTHONPATH Resolution Order**

```dockerfile
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:/app
```

**What happens:**
1. Python searches site-packages first
2. If `autochannel.ui` isn't there (or structured incorrectly), it falls back to `/app`
3. If `/app/autochannel/ui` doesn't exist or isn't structured correctly, the import fails

### 4. **Namespace Package Conflict**

Both packages install to the `autochannel` namespace:
- Bot package: `autochannel` (with `data/`, `lib/`, etc.)
- UI package: `autochannel/ui`

**The problem:**
- If the bot's `autochannel` package isn't set up as a namespace package, it might not allow subpackages
- Or the UI package might not be installing correctly to coexist with the bot package

## Why It Keeps Happening

The error persists because:

1. **The UI package might not be installing correctly** to site-packages
   - The build might succeed, but the installation might fail silently
   - The structure in site-packages might be wrong

2. **The source copy might be failing**
   - The path `/app/ui/autochannel/ui` might not exist in the builder stage
   - The copy might be happening before the UI source is in place

3. **The package structure might be incorrect**
   - The UI package expects `autochannel/ui` relative to `ui/pyproject.toml`
   - But the actual structure might be different

4. **Python's import system can't find it**
   - Even if the files exist, Python might not recognize them as a valid package
   - Missing `__init__.py` files or incorrect structure

## The Fix

The solution is to:
1. **Verify the UI package installs correctly** to site-packages
2. **Ensure the source is copied correctly** to `/app/autochannel/ui`
3. **Verify the structure is correct** (both `__init__.py` files exist)
4. **Test the import** during the build to catch issues early

The debug commands in the Dockerfile will help identify which of these is the actual problem.
