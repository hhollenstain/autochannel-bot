# Build from the repo root: docker build -f apps/bot/Dockerfile .
FROM python:3.14-alpine

RUN apk add gcc g++ musl-dev libffi-dev libxml2-dev libxslt-dev git make postgresql-dev
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Workspace metadata first so dependencies are cached independently of app code.
# Every member's pyproject.toml is needed for uv to read the shared lock.
COPY pyproject.toml uv.lock ./
COPY apps/bot/pyproject.toml apps/bot/README.md ./apps/bot/
COPY apps/ui/pyproject.toml ./apps/ui/
COPY packages/autochannel-db/pyproject.toml ./packages/autochannel-db/
RUN uv sync --frozen --no-dev --package autochannel --no-install-workspace

COPY packages ./packages
COPY apps/bot ./apps/bot
RUN uv sync --frozen --no-dev --package autochannel --no-editable

CMD ["autochannel"]
