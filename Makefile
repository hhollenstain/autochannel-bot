.PHONY: init check dist publish

init:
	# pipenv install git+https://github.com/Rapptz/discord.py@master#egg=discord.py
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
	# pip install -U git+https://github.com/Rapptz/discord.py@master#egg=discord.py
	pip install -e "."
