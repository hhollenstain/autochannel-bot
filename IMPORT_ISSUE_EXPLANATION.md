# Import Issue Explanation: `ModuleNotFoundError: No module named 'autochannel.ui'`

## Root Cause

The import error occurs because Python cannot find the `autochannel.ui` module. This happens due to a combination of package installation and import path issues:

### 1. **Package Installation Structure**
- The UI package's `pyproject.toml` specifies `packages = ["autochannel/ui"]`
- When installed, this creates `autochannel/ui` in site-packages
- However, for Python to import `autochannel.ui`, it needs:
  - `autochannel/__init__.py` (from bot package) ✅
  - `autochannel/ui/__init__.py` (from UI package) ❓

### 2. **Namespace Package Issue**
- The bot package installs `autochannel` to site-packages
- The UI package should install `autochannel/ui` to site-packages
- Both packages need to coexist in the same namespace
- If the UI package doesn't install correctly, or if the structure in site-packages is wrong, Python can't find it

### 3. **PYTHONPATH Resolution**
- `PYTHONPATH=/usr/local/lib/python3.10/site-packages:/app`
- Python searches site-packages first, then `/app`
- If the UI package isn't in site-packages correctly, Python falls back to `/app`
- But if `/app/autochannel/ui` doesn't exist or isn't structured correctly, the import fails

### 4. **Possible Causes**

**A. UI Package Not Installing Correctly**
- The UI package might not be installing `autochannel/ui` to site-packages
- The build process might be failing silently
- The package structure in the wheel might be incorrect

**B. Source Copy Issue**
- The source might not be copying correctly from builder to runtime
- The path `/app/ui/autochannel/ui` might not exist in the builder stage
- The copy command might be failing silently

**C. Namespace Package Conflict**
- The bot's `autochannel` package might not allow the UI subpackage
- There might be a conflict between the installed package and the source copy

## Solution

The fix ensures:
1. The UI package source is correctly copied to `/app/autochannel/ui`
2. The structure is verified during the build
3. Both the installed package (in site-packages) and source (in `/app`) are available
4. Python can find the module via either path

## Verification

To verify the fix works:
1. Check that `/app/autochannel/ui/__init__.py` exists
2. Check that `/app/autochannel/__init__.py` exists (from bot package)
3. Test import: `python3 -c "import autochannel.ui; print('SUCCESS')"`
4. Verify site-packages: Check if `autochannel/ui` exists in site-packages
