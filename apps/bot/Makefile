.PHONY: init check dist publish test

init:
	uv sync --dev

check: test
	uv run ruff format --check autochannel
	uv run ruff check autochannel
	uv run mypy --package autochannel --strict

test:
	uv sync --dev
	PYTHONPATH=. uv run python -c "from autochannel import VERSION; print(VERSION)"
	PYTHONPATH=. uv run python -c "import autochannel.autochannel_bot"
	PYTHONPATH=. uv run python -m pytest tests/ -v --tb=short

dist: init check
	uv build --package autochannel

test-full:
	uv sync --dev
	PYTHONPATH=. uv run python -c "from autochannel import VERSION; print(VERSION)"
	PYTHONPATH=. uv run python -c "import autochannel.autochannel_bot"
	PYTHONPATH=. uv run python -m pytest tests/ -v --tb=short --cov=autochannel --cov-report=term-missing