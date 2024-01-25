.PHONY: help clean clean-test clean-pyc clean-build help lint test playwright-shiny playwright-examples playwright-deploys install-trcli install-playwright
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
	match = re.match(r'^([a-zA-Z1-9_-]+):.*?## (.*)$$', line)
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

typings/matplotlib/__init__.pyi: ## grab type stubs from GitHub
	mkdir -p typings
	git clone --depth 1 https://github.com/microsoft/python-type-stubs typings/python-type-stubs
	mv typings/python-type-stubs/stubs/matplotlib typings/
	rm -rf typings/python-type-stubs

typings/seaborn:
	pyright --createstub seaborn

pyright: typings/uvicorn typings/matplotlib/__init__.pyi typings/seaborn ## type check with pyright
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
	python3 tests/pytest/asyncio_prevent.py
	pytest

# Default `SUB_FILE` to empty
SUB_FILE:=

install-playwright:
	playwright install --with-deps

install-trcli:
	which trcli || pip install trcli

install-rsconnect: ## install the main version of rsconnect till pypi version supports shiny express
	pip install git+https://github.com/rstudio/rsconnect-python.git#egg=rsconnect-python

playwright-shiny: install-playwright ## end-to-end tests with playwright
	pytest tests/playwright/shiny/$(SUB_FILE)

playwright-deploys: install-playwright install-rsconnect ## end-to-end tests on examples with playwright
	pytest tests/playwright/deploys/$(SUB_FILE)

playwright-examples: install-playwright ## end-to-end tests on examples with playwright
	pytest tests/playwright/examples/$(SUB_FILE)

testrail-junit: install-playwright install-trcli ## end-to-end tests with playwright and generate junit report
	pytest tests/playwright/shiny/$(SUB_FILE) --junitxml=report.xml

coverage: ## check combined code coverage (must run e2e last)
	pytest --cov-report term-missing --cov=shiny tests/pytest/ tests/playwright/shiny/$(SUB_FILE)
	coverage html
	$(BROWSER) htmlcov/index.html

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

install-deps: ## install dependencies
	pip install -e ".[dev,test]" --upgrade

# ## If caching is ever used, we could run:
# install-deps: ## install latest dependencies
# 	pip install --editable ".[dev,test]" --upgrade --upgrade-strategy eager
