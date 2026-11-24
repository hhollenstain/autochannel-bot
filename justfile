install:
    uv sync
    cd frontend && npm ci

# Flask API on :5000. In dev, set FRONTEND_URL=http://localhost:5173 so OAuth returns to Vite.
api:
    uv run autochannel_ui --debug

web:
    cd frontend && npm run dev

test:
    uv run ruff check .
    uv run pytest
    cd frontend && npm run typecheck && npm test

build-web:
    cd frontend && npm run build

migrate:
    uv run alembic -c packages/autochannel-db/alembic.ini upgrade head

docker-compose: build-image
    op run --env-file=.env-dev -- docker compose up

build-image:
    docker build -t hhollenstain/autochannel-ui:latest .
