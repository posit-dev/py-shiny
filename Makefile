# .PHONY: help clean% check% format% docs% lint test pyright playwright% install% testrail% coverage release

# Depend on `FORCE` to ensure the target is always run
FORCE:

# TODO-barret; Use `pybin/activate && COMMAND` approach, not `$(COMMAND)` approach

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


BROWSER := $(PYTHON) -c "$$BROWSER_PYSCRIPT"

help: $(PYTHON) FORCE
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


# Gather python3 version; Ex: `3.11`
PYTHON_VERSION := $(shell python3 -c "from platform import python_version; print(python_version().rsplit('.', 1)[0])")

# -----------------
# File paths for common executables / paths
# -----------------

VENV = .venv
# VENV = .venv-$(PYTHON_VERSION)
PYBIN = $(VENV)/bin
PIP = $(PYBIN)/pip
PYTHON = $(PYBIN)/python
UV = $(PYBIN)/uv
PYBIN_ACTIVATE = $(PYBIN)/activate
SITE_PACKAGES=$(VENV)/lib/python$(PYTHON_VERSION)/site-packages

# /----------------



# -----------------
# Core virtual environment and installing
# -----------------

# Any targets that depend on $(VENV) or $(PYBIN) will cause the venv to be
# created. To use the venv, python scripts should run with the prefix $(PYBIN),
# as in `$(PYBIN)/pip`.
$(VENV):
	@echo "-------- Making virtual environment: $(VENV) --------"
	python3 -m venv $(VENV)
	$(PYBIN)/pip install --upgrade pip

$(PYBIN): $(VENV)
$(PYBIN_ACTIVATE): $(PYBIN)
$(PIP): $(PYBIN)

UV_PKG = $(SITE_PACKAGES)/uv
$(UV): $(UV_PKG)
$(UV_PKG): $(PIP)
	@echo "-------- Installing uv --------"
	$(PIP) install uv # avoid circular dependency

# /----------------

# -----------------
# Python package executables
# -----------------
# Use `FOO=$(PYBIN)/foo` to define the path to a package's executable
# Use `FOO_PKG=$(SITE_PACKAGES)/foo` to define the path to a package's site-packages directory

# Depend on `$(FOO_PKG)` to ensure the package is installed,
# but use `$(FOO)` to actually run the package's executable

# BLACK = $(PYTHON) -m black
BLACK_PKG = $(SITE_PACKAGES)/black
ISORT = $(PYBIN)/isort
ISORT_PKG = $(SITE_PACKAGES)/isort
FLAKE8 = $(PYBIN)/flake8
FLAKE8_PKG = $(SITE_PACKAGES)/flake8
PYTEST = $(PYBIN)/pytest
PYTEST_PKG = $(SITE_PACKAGES)/pytest
COVERAGE = $(PYBIN)/coverage
COVERAGE_PKG = $(SITE_PACKAGES)/coverage
PYRIGHT = $(PYBIN)/pyright
PYRIGHT_PKG = $(SITE_PACKAGES)/pyright
PLAYWRIGHT = $(PYBIN)/playwright
PLAYWRIGHT_PKG = $(SITE_PACKAGES)/playwright
$(BLACK_PKG) $(ISORT_PKG) $(FLAKE8_PKG) $(PYTEST_PKG) $(COVERAGE_PKG) $(PYRIGHT_PKG) $(PLAYWRIGHT_PKG):
	@$(MAKE) install-deps
# 	touch $@ # update timestamp of target file

# /----------------

# -----------------
# Helper packages not defined in `setup.cfg`
# -----------------

TRCLI_PKG = $(SITE_PACKAGES)/trcli
$(TRCLI_PKG):
	@$(MAKE) $(UV)
	@echo "-------- Installing trcli --------"
	$(UV) pip install trcli
	# @touch $(PYBIN)/trcli # update timestamp

TWINE_PKG = $(SITE_PACKAGES)/twine
$(TWINE_PKG):
	@$(MAKE) $(UV)
	@echo "-------- Installing twine --------"
	$(UV) pip install twine
	# @touch $(PYBIN)/twine # update timestamp

RSCONNECT_PKG = $(SITE_PACKAGES)/rsconnect
$(RSCONNECT_PKG): ## install the main version of rsconnect till pypi version supports shiny express
	@$(MAKE) $(UV)
	$(UV) pip install rsconnect @ git+https://github.com/rstudio/rsconnect-python.git

# /----------------

# -----------------
# Type stubs
# -----------------

typings/uvicorn: $(PYRIGHT_PKG)
	@echo "-------- Creating stub for uvicorn --------"
	$(PYRIGHT) --createstub uvicorn

typings/matplotlib/__init__.pyi: ## grab type stubs from GitHub
	@echo "-------- Creating stub for matplotlib --------"
	mkdir -p typings
	git clone --depth 1 https://github.com/microsoft/python-type-stubs typings/python-type-stubs
	mv typings/python-type-stubs/stubs/matplotlib typings/
	rm -rf typings/python-type-stubs

typings/seaborn: $(PYRIGHT_PKG)
	@echo "-------- Creating stub for seaborn --------"
	$(PYRIGHT) --createstub seaborn

pyright-typings: typings/uvicorn typings/matplotlib/__init__.pyi typings/seaborn
# /----------------


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: FORCE ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: FORCE ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: FORCE ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -rf typings/



check: check-lint check-types check-tests ## check code, style, types, and test (basic CI)
check-fix: format check-lint check-types check-tests ## check and format code, style, types, and test
check-lint: check-ruff ## check code formatting and style

check-ruff: $(PYBIN) FORCE
	@echo "-------- Running ruff lint and formatting checks --------"
	@# Check imports in addition to code
	@# Reason for two commands: https://github.com/astral-sh/ruff/issues/8232
	# $(PYBIN)/ruff check --select I .
	# Check lints
	$(PYBIN)/ruff check .
	# Check formatting
	$(PYBIN)/ruff format --check .
check-types: pyright-typings $(PYRIGHT_PKG) FORCE
	@echo "-------- Checking types with pyright --------"
	$(PYBIN)/pyright
check-tests: $(PYTEST_PKG) FORCE
	@echo "-------- Running tests with pytest --------"
	$(PYTHON) tests/pytest/asyncio_prevent.py
	$(PYTEST)


pyright: check-types ## check types with pyright
lint: check-lint ## check style with flake8
test: check-tests ## check tests quickly with the default Python

format: format-ruff ## format code

format-ruff: $(PYBIN) FORCE
	@echo "-------- Formatting code with ruff --------"
	@# Reason for two commands: https://github.com/astral-sh/ruff/issues/8232
	@# Fix imports
	$(PYBIN)/ruff check --select I --fix .
	@# Fix formatting
	$(PYBIN)/ruff format .


# format: format-black format-isort ## format code with black and isort
# format-black: $(BLACK_PKG) FORCE
# 	@echo "-------- Formatting code with black --------"
# 	$(PYTHON) -m black .
# format-isort: $(ISORT_PKG) FORCE
# 	@echo "-------- Sorting imports with isort --------"
# 	$(ISORT) .

docs: FORCE ## docs: build docs with quartodoc
	@echo "-------- Building docs with quartodoc --------"
	@cd docs && make quartodoc

docs-preview: FORCE ## docs: preview docs in browser
	@echo "-------- Previewing docs in browser --------"
	@cd docs && make serve

# Default `SUB_FILE` to empty
SUB_FILE:=

install-playwright: $(PLAYWRIGHT_PKG) FORCE
	@echo "-------- Installing playwright browsers --------"
	@$(PLAYWRIGHT) install --with-deps

playwright-shiny: install-playwright $(PYTEST_PKG) FORCE ## end-to-end tests with playwright
	$(PYTEST) tests/playwright/shiny/$(SUB_FILE)

playwright-deploys: install-playwright $(RSCONNECT_PKG) $(PYTEST_PKG) FORCE ## end-to-end tests on examples with playwright
	$(PYTEST) tests/playwright/deploys/$(SUB_FILE)

playwright-examples: install-playwright $(PYTEST_PKG) FORCE ## end-to-end tests on examples with playwright
	$(PYTEST) tests/playwright/examples/$(SUB_FILE)

playwright-debug: install-playwright $(PYTEST_PKG) FORCE ## All end-to-end tests, chrome only, headed
	$(PYTEST) -c tests/playwright/playwright-pytest.ini tests/playwright/$(SUB_FILE)

playwright-show-trace: FORCE ## Show trace of failed tests
	npx playwright show-trace test-results/*/trace.zip

testrail-junit: install-playwright $(TRCLI_PKG) $(PYTEST_PKG) FORCE ## end-to-end tests with playwright and generate junit report
	$(PYTEST) tests/playwright/shiny/$(SUB_FILE) --junitxml=report.xml

coverage: $(PYTEST_PKG) $(COVERAGE_PKG) FORCE ## check combined code coverage (must run e2e last)
	$(PYTEST) --cov-report term-missing --cov=shiny tests/pytest/ tests/playwright/shiny/$(SUB_FILE)
	$(PYBIN)/coverage html
	$(BROWSER) htmlcov/index.html

release: $(TWINE_PKG) dist FORCE ## package and upload a release
	$(PYBIN)/twine upload dist/*

dist: clean $(PYTHON) FORCE ## builds source and wheel package
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel
	ls -l dist

## install the package to the active Python's site-packages
# Note that instead of --force-reinstall, we uninstall and then install, because
# --force-reinstall also reinstalls all deps. And if we also used --no-deps, then the
# deps wouldn't be installed the first time.
install: dist $(PIP) FORCE
	$(PIP) uninstall -y shiny
	$(PIP) install dist/shiny*.whl

install-deps: $(UV) FORCE ## install dependencies
	$(UV) pip install -e ".[dev,test]" --refresh

# ## If caching is ever used, we could run:
# install-deps: ## install latest dependencies
# 	pip install --editable ".[dev,test]" --upgrade --upgrade-strategy eager
