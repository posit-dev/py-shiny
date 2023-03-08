.PHONY: help clean clean-test clean-pyc clean-build docs help lint test e2e test-all
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -rf typings/

typings/uvicorn:
	pyright --createstub uvicorn

typings/matplotlib:
	pyright --createstub matplotlib

pyright: typings/uvicorn typings/matplotlib ## type check with pyright
	pyright

lint: ## check style with flake8
	echo "Checking style with flake8."
	flake8 --show-source .

format: ## format code with black and isort
	echo "Formatting code with black."
	black .
	echo "Sorting imports with isort."
	isort .

check: ## check code quality with black and isort
	echo "Checking code with black."
	black --check .
	echo "Sorting imports with isort."
	isort --check-only --diff .

test: ## run tests quickly with the default Python
	python3 tests/asyncio_prevent.py
	pytest

e2e: ## run e2e tests with playwright
	tox

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source shiny -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/shiny.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ shiny
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

## install the package to the active Python's site-packages
# Note that instead of --force-reinstall, we uninstall and then install, because
# --force-reinstall also reinstalls all deps. And if we also used --no-deps, then the
# deps wouldn't be installed the first time.
install: dist
	pip uninstall -y shiny
	python3 -m pip install dist/shiny*.whl
