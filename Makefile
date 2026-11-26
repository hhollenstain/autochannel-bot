# Monorepo entry points. Each app also has its own Makefile under apps/<app>/.
#
# Docker targets run the root docker-compose.yml against images built here as :local.
# Commands that need secrets (the compose targets and migrate) run under the 1Password
# CLI by default, resolving the op:// references in OP_ENV_FILE. To use plain env vars
# or a root .env instead, turn it off with RUN=, e.g. `make up RUN=`.
# Pass compose flags with UP_FLAGS, e.g. `make up-bot UP_FLAGS=-d`.
.PHONY: help install test test-bot test-ui migrate \
	build-images build-bot build-ui up up-bot up-ui down logs

IMAGE_PREFIX ?= hhollenstain
OP_ENV_FILE ?= apps/ui/.env-dev
RUN ?= op run --env-file=$(OP_ENV_FILE) --
UP_FLAGS ?=
# Which image runs `alembic upgrade head` in the compose `migrate` service.
MIGRATE_APP ?= autochannel-ui
# Separate compose project, so local test stacks never touch a deployment started from
# this directory with plain `docker compose up`.
COMPOSE_PROJECT ?= autochannel-local
COMPOSE = $(RUN) env AUTOCHANNEL_TAG=local AUTOCHANNEL_IMAGE_PREFIX=$(IMAGE_PREFIX) \
	AUTOCHANNEL_MIGRATE_APP=$(MIGRATE_APP) docker compose -p $(COMPOSE_PROJECT)

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

migrate: ## alembic upgrade head against SQLALCHEMY_DATABASE_URI (local venv, no Docker)
	$(RUN) uv run alembic -c packages/autochannel-db/alembic.ini upgrade head

build-images: build-bot build-ui ## Build both images, tagged :local

build-bot: ## Build only the bot image (:local)
	docker build -f apps/bot/Dockerfile -t $(IMAGE_PREFIX)/autochannel-bot:local .

build-ui: ## Build only the UI image (:local)
	docker build -f apps/ui/Dockerfile -t $(IMAGE_PREFIX)/autochannel-ui:local .

up: build-images ## Rebuild both images and run migrate + bot + ui together
	$(COMPOSE) up $(UP_FLAGS) migrate bot ui

# Migrations run from the bot image, so the UI image doesn't have to exist. If the full
# stack is already running, this only recreates the bot container.
up-bot: build-bot ## Rebuild only the bot image and run migrate + bot
	$(COMPOSE) up $(UP_FLAGS) migrate bot
up-bot: MIGRATE_APP = autochannel-bot

up-ui: build-ui ## Rebuild only the UI image and run migrate + ui
	$(COMPOSE) up $(UP_FLAGS) migrate ui

down: ## Stop and remove the compose stack
	$(COMPOSE) down

logs: ## Follow logs for the running stack
	$(COMPOSE) logs -f
