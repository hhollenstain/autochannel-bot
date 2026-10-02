.PHONY: init check dist publish test

PIPENV = PIPENV_IGNORE_VIRTUALENVS=1 pipenv

init:
	$(PIPENV) install --dev

check: test
	$(PIPENV) run ruff check setup.py autochannel

test:
	$(PIPENV) install --dev
	PYTHONPATH=. $(PIPENV) run python -c "from autochannel import VERSION; print(VERSION)"
	PYTHONPATH=. $(PIPENV) run python -c "import autochannel.autochannel_bot"

dist: init check
	$(PIPENV) run python setup.py sdist bdist_wheel

live:
	pip install -e "."
