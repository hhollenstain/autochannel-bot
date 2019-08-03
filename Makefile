.PHONY: init check dist publish

init:
	pipenv install -e "."
	pipenv run python setup.py develop

check: test
	#pipenv check
	pipenv run pylint setup.py
	#pipenv run pylint autochannel/*.py

test:
	pipenv install -e ".[test]"
	pipenv run python setup.py develop

dist: init check req
	pipenv run python setup.py sdist bdist_wheel install

live:
	pip install -e "."
