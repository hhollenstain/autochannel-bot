.PHONY: init check dist publish

init:
	uv sync
	uv pip install -e "."

check: test
	uv run pylint setup.py
	#uv run pylint autochannel/*.py

test:
	uv sync --extra test
	uv pip install -e "."

dist: init check req
	uv build

live:
	uv pip install -e "."
