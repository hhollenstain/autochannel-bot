FROM node:24-alpine AS frontend

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Dependencies first so they're cached independently of app code.
COPY pyproject.toml uv.lock README.md ./
COPY packages ./packages
RUN uv sync --frozen --no-dev --no-install-project

COPY autochannel ./autochannel
RUN uv sync --frozen --no-dev

COPY --from=frontend /app/frontend/dist ./frontend/dist

EXPOSE 5000
CMD ["autochannel_ui"]
