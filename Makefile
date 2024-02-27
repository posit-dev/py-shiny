.PHONY: help clean% check% format% docs% lint test pyright playwright% install% testrail% coverage release
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

typings/appdirs:
	echo "Creating appdirs stubs"
	pyright --createstub appdirs
typings/folium:
	echo "Creating folium stubs"
	pyright --createstub folium
typings/uvicorn:
	echo "Creating uvicorn stubs"
	pyright --createstub uvicorn
typings/seaborn:
	echo "Creating seaborn stubs"
	pyright --createstub seaborn

typings/matplotlib/__init__.pyi:
	echo "Creating matplotlib stubs"
	mkdir -p typings
	git clone --depth 1 https://github.com/microsoft/python-type-stubs typings/python-type-stubs
	mv typings/python-type-stubs/stubs/matplotlib typings/
	rm -rf typings/python-type-stubs

pyright-typings: typings/appdirs typings/folium typings/uvicorn typings/seaborn typings/matplotlib/__init__.pyi

check: check-format check-lint check-types check-tests  ## check code, style, types, and test (basic CI)
check-fix: format check-lint check-types check-tests ## check and format code, style, types, and test
check-format: check-black check-isort
check-types: check-pyright
check-tests: check-pytest

check-lint:
	@echo "-------- Checking style with flake8 ---------"
	flake8 --show-source .
check-black:
	@echo "-------- Checking code with black -----------"
	black --check .
check-isort:
	@echo "-------- Sorting imports with isort ---------"
	isort --check-only --diff .
check-pyright: typings/uvicorn typings/matplotlib/__init__.pyi typings/seaborn
	@echo "-------- Checking types with pyright --------"
	pyright
check-pytest:
	@echo "-------- Running tests with pytest ----------"
	python3 tests/pytest/asyncio_prevent.py
	pytest

pyright: check-types ## check types with pyright
lint: check-lint ## check style with flake8
test: check-tests ## check tests quickly with the default Python

format: format-black format-isort ## format code with black and isort
format-black:
	@echo "-------- Formatting code with black --------"
	black .
format-isort:
	@echo "-------- Sorting imports with isort --------"
	isort .

docs: ## docs: build docs with quartodoc
	@echo "-------- Building docs with quartodoc --------"
	@cd docs && make quartodoc

docs-preview: ## docs: preview docs in browser
	@echo "-------- Previewing docs in browser --------"
	@cd docs && make serve

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

playwright-debug: install-playwright ## All end-to-end tests, chrome only, headed
	pytest -c tests/playwright/playwright-pytest.ini tests/playwright/$(SUB_FILE)

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
