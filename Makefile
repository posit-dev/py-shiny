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


PYTHON_VERSION := $(shell python3 -c "from platform import python_version; print(python_version())")
VENV = .venv-$(PYTHON_VERSION)
PYBIN = $(VENV)/bin
PIP = $(PYBIN)/pip
UV = $(PYBIN)/uv
PYBIN_ACTIVATE = $(PYBIN)/activate


# Any targets that depend on $(VENV) or $(PYBIN) will cause the venv to be
# created. To use the venv, python scripts should run with the prefix $(PYBIN),
# as in `$(PYBIN)/pip`.
$(VENV):
	python3 -m venv $(VENV)

$(PYBIN): $(VENV)
$(PYBIN_ACTIVATE): $(PYBIN)

$(UV): install-deps
	touch $(UV) # update timestamp

$(PYBIN)/flake8: install-deps
  touch $(PYBIN)/flake8 # update timestamp
$(PYBIN)/black: install-deps
  touch $(PYBIN)/black # update timestamp
$(PYBIN)/isort: install-deps
  touch $(PYBIN)/isort # update timestamp
$(PYBIN)/pytest: install-deps
  touch $(PYBIN)/pytest # update timestamp
$(PYBIN)/coverage: install-deps
  touch $(PYBIN)/coverage # update timestamp
$(PYBIN)/pyright: install-deps
  touch $(PYBIN)/pyright # update timestamp
$(PYBIN)/playwright: install-deps
  touch $(PYBIN)/playwright # update timestamp


$(PYBIN)/trcli: $(UV)
	$(UV) pip install trcli
	touch $(PYBIN)/trcli # update timestamp
$(PYBIN)/twine: $(UV)
	$(UV) pip install twine
	touch $(PYBIN)/twine # update timestamp


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

check: check-format check-lint check-types check-tests  ## check code, style, types, and test (basic CI)
check-fix: format check-lint check-types check-tests ## check and format code, style, types, and test
check-format: check-black check-isort
check-lint: $(PYBIN)/flake8
	@echo "-------- Checking style with flake8 --------"
	$(PYBIN)/flake8 --show-source .
check-black: $(PYBIN)/black
	@echo "-------- Checking code with black --------"
	$(PYBIN)/black --check .
check-isort: $(PYBIN)/isort
	@echo "-------- Sorting imports with isort --------"
	$(PYBIN)/isort --check-only --diff .
check-types: typings/uvicorn typings/matplotlib/__init__.pyi typings/seaborn $(PYBIN)/pyright
	@echo "-------- Checking types with pyright --------"
	$(PYBIN)/pyright
check-tests: $(PYBIN)/pytest $(PYBIN)
	@echo "-------- Running tests with pytest --------"
	$(PYBIN)/python tests/pytest/asyncio_prevent.py
	$(PYBIN)/pytest

pyright: check-types ## check types with pyright
lint: check-lint ## check style with flake8
test: check-tests ## check tests quickly with the default Python

format: format-black format-isort ## format code with black and isort
format-black: $(PYBIN)/black
	@echo "-------- Formatting code with black --------"
	$(PYBIN)/black .
format-isort: $(PYBIN)/isort
	@echo "-------- Sorting imports with isort --------"
	$(PYBIN)/isort .

docs: ## docs: build docs with quartodoc
	@echo "-------- Building docs with quartodoc --------"
	@cd docs && make quartodoc

docs-preview: ## docs: preview docs in browser
	@echo "-------- Previewing docs in browser --------"
	@cd docs && make serve

# Default `SUB_FILE` to empty
SUB_FILE:=

install-playwright: $(PYBIN)/playwright $(PYBIN)/pytest
	$(PYBIN)/playwright install --with-deps

install-rsconnect: $(UV) ## install the main version of rsconnect till pypi version supports shiny express
	$(UV) pip install rsconnect @ git+https://github.com/rstudio/rsconnect-python.git

playwright-shiny: install-playwright $(PYBIN)/pytest ## end-to-end tests with playwright
	$(PYBIN)/pytest tests/playwright/shiny/$(SUB_FILE)

playwright-deploys: install-playwright install-rsconnect $(PYBIN)/pytest ## end-to-end tests on examples with playwright
	$(PYBIN)/pytest tests/playwright/deploys/$(SUB_FILE)

playwright-examples: install-playwright $(PYBIN)/pytest ## end-to-end tests on examples with playwright
	$(PYBIN)/pytest tests/playwright/examples/$(SUB_FILE)

playwright-debug: install-playwright $(PYBIN)/pytest ## All end-to-end tests, chrome only, headed
	$(PYBIN)/pytest -c tests/playwright/playwright-pytest.ini tests/playwright/$(SUB_FILE)

playwright-show-trace: ## Show trace of failed tests
	npx playwright show-trace test-results/*/trace.zip

testrail-junit: install-playwright $(PYBIN)/trcli $(PYBIN)/pytest ## end-to-end tests with playwright and generate junit report
	$(PYBIN)/pytest tests/playwright/shiny/$(SUB_FILE) --junitxml=report.xml

coverage: $(PYBIN)/pytest $(PYBIN)/coverage ## check combined code coverage (must run e2e last)
	$(PYBIN)/pytest --cov-report term-missing --cov=shiny tests/pytest/ tests/playwright/shiny/$(SUB_FILE)
	$(PYBIN)/coverage html
	$(BROWSER) htmlcov/index.html

release: $(PYBIN)/twine dist ## package and upload a release
	$(PYBIN)/twine upload dist/*

dist: clean $(PYBIN) $(PYBIN)/pytest ## builds source and wheel package
	$(PYBIN)/python setup.py sdist \
	$(PYBIN)/pytest setup.py bdist_wheel \
	ls -l dist

## install the package to the active Python's site-packages
# Note that instead of --force-reinstall, we uninstall and then install, because
# --force-reinstall also reinstalls all deps. And if we also used --no-deps, then the
# deps wouldn't be installed the first time.
install: dist $(UV)
	$(UV) pip uninstall -y shiny
	$(PYBIN)/python -m pip install dist/shiny*.whl

install-deps: $(UV) ## install dependencies
	$(UV) pip install -e ".[dev,test]" --refresh

# ## If caching is ever used, we could run:
# install-deps: ## install latest dependencies
# 	pip install --editable ".[dev,test]" --upgrade --upgrade-strategy eager
