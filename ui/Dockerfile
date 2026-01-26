# Build stage: Install dependencies using UV
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc g++ musl-dev libffi-dev libxml2-dev libxslt-dev git postgresql-dev curl

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

WORKDIR /app

# Copy bot's autochannel package first (needed for shared models)
COPY autochannel ./autochannel

# Copy UI dependency files (for better Docker layer caching)
COPY ui/pyproject.toml ./
# Generate lock file if needed
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock || true

# Copy UI application source into autochannel/ui (so it becomes autochannel.ui package)
COPY ui/autochannel/ui ./autochannel/ui
COPY ui/run.py ./run.py
COPY ui/manage.py ./manage.py

# Install UI package and dependencies using UV pip (system-wide installation)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache .

# Runtime stage: Minimal image with only runtime dependencies
FROM python:3.10-alpine AS runtime

# Install only runtime system dependencies (no build tools needed)
RUN apk add --no-cache libffi libxml2 libxslt postgresql-libs

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy installed binaries (like the autochannel_ui entry point)
COPY --from=builder /usr/local/bin/autochannel_ui /usr/local/bin/autochannel_ui

# Copy bot's autochannel package (for shared models) and UI code (autochannel.ui)
COPY --from=builder /app/autochannel /app/autochannel
COPY --from=builder /app/run.py /app/run.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:/app

# Expose port
EXPOSE 5000

# Run the application
CMD ["autochannel_ui"]
