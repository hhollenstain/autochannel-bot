# Build stage: Install dependencies using UV
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc g++ musl-dev libffi-dev libxml2-dev libxslt-dev git postgresql-dev curl

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

WORKDIR /app

# Copy bot dependency files first (for better Docker layer caching)
COPY pyproject.toml ./

# Generate lock file for bot if needed
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock || true

# Copy bot application source
COPY autochannel ./autochannel

# Install bot package and dependencies using UV pip (system-wide installation)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache .

# Copy UI dependency files and source
# The UI package expects autochannel/ui relative to ui/pyproject.toml
# We need to ensure autochannel exists as a parent package
COPY ui/pyproject.toml ./ui/
# Create autochannel parent directory in ui/ for the package structure
RUN mkdir -p ./ui/autochannel
# Copy the UI source into the autochannel/ui subdirectory
COPY ui/autochannel/ui ./ui/autochannel/ui
COPY ui/run.py ./ui/run.py
COPY ui/manage.py ./ui/manage.py

# Generate lock file for UI if needed
RUN --mount=type=cache,target=/root/.cache/uv \
    cd ui && uv lock || true

# Install UI package and dependencies using UV pip (system-wide installation)
# The pyproject.toml is in ui/ directory, so we need to install from there
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache ./ui
# Verify the UI package was installed correctly
RUN python3 -c "import sys; import os; sp = [p for p in sys.path if 'site-packages' in p][0]; ui_path = os.path.join(sp, 'autochannel', 'ui'); print(f'UI package in site-packages: {os.path.exists(ui_path)}'); print(f'Path: {ui_path}')" 2>&1 || echo "WARNING: Could not verify UI package installation"

# Runtime stage: Minimal image with only runtime dependencies
FROM python:3.10-alpine AS runtime

# Install only runtime system dependencies (no build tools needed)
RUN apk add --no-cache libffi libxml2 libxslt postgresql-libs

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy installed binaries (both bot and UI entry points)
COPY --from=builder /usr/local/bin/autochannel /usr/local/bin/autochannel
COPY --from=builder /usr/local/bin/autochannel_ui /usr/local/bin/autochannel_ui

# Copy application source (bot and UI)
# Both packages are installed to site-packages, but we also need source in /app for imports
COPY --from=builder /app/autochannel /app/autochannel
# Copy UI package source to autochannel/ui so it's available as autochannel.ui
# The UI package installs to site-packages, but we also need source in /app for direct imports
# Ensure the directory exists before copying
RUN mkdir -p /app/autochannel
# Copy the entire UI package structure (autochannel/ui) to /app/autochannel/ui
# CRITICAL: The UI package installs to site-packages, but we MUST also have source in /app
# because Python's import system needs it to be accessible via PYTHONPATH
COPY --from=builder /app/ui/autochannel/ui /app/autochannel/ui
# Verify the structure is correct - both __init__.py files must exist
RUN test -f /app/autochannel/__init__.py || (echo "ERROR: /app/autochannel/__init__.py missing" && exit 1)
RUN test -f /app/autochannel/ui/__init__.py || (echo "ERROR: /app/autochannel/ui/__init__.py missing" && exit 1)
# Verify key UI files exist (don't import - requires env vars at import time)
RUN test -f /app/autochannel/ui/config.py && test -d /app/autochannel/ui/lib && echo "UI package structure verified" || (echo "ERROR: UI package structure incomplete" && ls -la /app/autochannel/ui/ && exit 1)
# Copy UI run.py to /app for the entry point to work (entry point expects 'run' module)
COPY --from=builder /app/ui/run.py /app/run.py
COPY --from=builder /app/ui/manage.py /app/manage.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
# CRITICAL: /app must come FIRST in PYTHONPATH
# Python finds 'autochannel' in site-packages (bot package) which doesn't have 'ui' subpackage
# By putting /app first, Python finds /app/autochannel which has BOTH bot code AND ui code
ENV PYTHONPATH=/app:/usr/local/lib/python3.10/site-packages

# Expose ports (bot doesn't need one, UI uses 5000)
EXPOSE 5000

# Default to running bot (can be overridden in docker-compose)
CMD ["autochannel"]
