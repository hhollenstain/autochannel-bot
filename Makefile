.PHONY: init check dist publish test

init:
	uv sync --dev

check: test
	uv run ruff check setup.py autochannel

test:
	uv sync --dev
	PYTHONPATH=. uv run python -c "from autochannel import VERSION; print(VERSION)"
	PYTHONPATH=. uv run python -c "import autochannel.autochannel_bot"

dist: init check
	uv run python setup.py sdist bdist_wheel

live:
	uv pip install -e ".[dev]"
