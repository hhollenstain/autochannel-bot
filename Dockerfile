# Build stage: Install dependencies using UV
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc g++ musl-dev libffi-dev libxml2-dev libxslt-dev git postgresql-dev curl

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

WORKDIR /app

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml ./

# Generate lock file if needed (for reproducible builds)
# Using cache mount for UV's global cache to speed up builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock || true

# Copy application source
COPY . .

# Install package and dependencies using UV pip (system-wide installation)
# This installs directly into /usr/local for copying to runtime stage
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache .

# Runtime stage: Minimal image with only runtime dependencies
FROM python:3.10-alpine AS runtime

# Install only runtime system dependencies (no build tools needed)
RUN apk add --no-cache libffi libxml2 libxslt postgresql-libs

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy installed binaries (like the autochannel entry point)
COPY --from=builder /usr/local/bin/autochannel /usr/local/bin/autochannel

# Copy application source (needed for some imports/paths)
COPY --from=builder /app/autochannel /app/autochannel

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:/app

# Run the application
CMD ["autochannel"]
