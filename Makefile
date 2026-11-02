.PHONY: init check dist publish test

init:
	uv sync --dev

check: test
	uv run ruff check setup.py autochannel

test:
	uv sync --dev
	PYTHONPATH=. uv run python -c "from autochannel import VERSION; print(VERSION)"
	PYTHONPATH=. uv run python -c "import autochannel.autochannel_bot"
	PYTHONPATH=. uv run python -m pytest tests/ -v --tb=short

dist: init check
	uv run python setup.py sdist bdist_wheel

live:
	uv pip install -e ".[dev]"

test-full:
	uv sync --dev
	PYTHONPATH=. uv run python -c "from autochannel import VERSION; print(VERSION)"
	PYTHONPATH=. uv run python -c "import autochannel.autochannel_bot"
	PYTHONPATH=. uv run python -m pytest tests/ -v --tb=short