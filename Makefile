# Monorepo entry points. Each app also has its own Makefile under apps/<app>/.
.PHONY: help install test test-bot test-ui migrate build-images

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-14s %s\n", $$1, $$2}'

install: ## uv sync every workspace member + npm ci for the UI frontend
	uv sync --all-packages
	cd apps/ui/frontend && npm ci

test: test-bot test-ui ## Run every app's checks

test-bot: ## Bot: ruff, mypy --strict, pytest
	$(MAKE) -C apps/bot check

test-ui: ## UI: ruff, pytest, frontend typecheck + tests
	$(MAKE) -C apps/ui test

migrate: ## alembic upgrade head against SQLALCHEMY_DATABASE_URI
	uv run alembic -c packages/autochannel-db/alembic.ini upgrade head

build-images: ## Build both images from the repo root
	docker build -f apps/bot/Dockerfile -t autochannel-bot:local .
	docker build -f apps/ui/Dockerfile -t autochannel-ui:local .
