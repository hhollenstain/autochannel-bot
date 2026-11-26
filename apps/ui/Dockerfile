# Build from the repo root: docker build -f apps/ui/Dockerfile .
FROM node:24-alpine AS frontend

WORKDIR /app/frontend
COPY apps/ui/frontend/package.json apps/ui/frontend/package-lock.json ./
RUN npm ci
COPY apps/ui/frontend/ ./
RUN npm run build


FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" \
    FRONTEND_DIST=/app/frontend/dist

WORKDIR /app

# Workspace metadata first so dependencies are cached independently of app code.
# Every member's pyproject.toml is needed for uv to read the shared lock.
COPY pyproject.toml uv.lock ./
COPY apps/ui/pyproject.toml apps/ui/README.md ./apps/ui/
COPY apps/bot/pyproject.toml ./apps/bot/
COPY packages/autochannel-db/pyproject.toml ./packages/autochannel-db/
RUN uv sync --frozen --no-dev --package autochannel-ui --no-install-workspace

COPY packages ./packages
COPY apps/ui/autochannel_ui ./apps/ui/autochannel_ui
RUN uv sync --frozen --no-dev --package autochannel-ui --no-editable

COPY --from=frontend /app/frontend/dist ./frontend/dist

EXPOSE 5000
CMD ["autochannel_ui"]
