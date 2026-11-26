.PHONY: help install api web test e2e build-web migrate docker-compose build-image

IMAGE ?= hhollenstain/autochannel-ui:latest

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-16s %s\n", $$1, $$2}'

install: ## uv sync + npm ci
	uv sync
	cd frontend && npm ci

# In dev, set FRONTEND_URL=http://localhost:5173 so OAuth returns to Vite.
api: ## Flask API on :5000
	uv run autochannel_ui --debug

web: ## Vite dev server on :5173
	cd frontend && npm run dev

test: ## ruff + pytest + frontend typecheck/tests
	uv run ruff check .
	uv run pytest
	cd frontend && npm run typecheck && npm test

e2e: ## Playwright browser tests against the built SPA with /api mocked; screenshots -> frontend/e2e/screenshots/
	cd frontend && npm run test:e2e

build-web: ## Build the frontend
	cd frontend && npm run build

migrate: ## alembic upgrade head
	uv run alembic -c ../../packages/autochannel-db/alembic.ini upgrade head

docker-compose: ## Build both images and run the full stack (root docker-compose.yml) with secrets from 1Password
	$(MAKE) -C ../.. up RUN="op run --env-file=apps/ui/.env-dev --"

build-image: ## Build the Docker image
	docker build -f Dockerfile -t $(IMAGE) ../..
