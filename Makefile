# https://www.gnu.org/software/make/manual/make.html#Phony-Targets
# Prerequisites of .PHONY are always interpreted as literal target names, never as patterns (even if they contain ‘%’ characters).
# # .PHONY: help clean% check% format% docs% lint test pyright playwright% install% testrail% coverage release js-*
# Using `FORCE` as prerequisite to _force_ the target to always run; https://www.gnu.org/software/make/manual/make.html#index-FORCE
FORCE:

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

help: FORCE
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


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
SITE_PACKAGES=$(VENV)/lib/python$(PYTHON_VERSION)/site-packages

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
$(PYTHON): $(PYBIN)
$(PIP): $(PYBIN)

UV = $(SITE_PACKAGES)/uv
$(UV):
	$(MAKE) $(PYBIN)
	@echo "-------- Installing uv --------"
	. $(PYBIN)/activate && \
	  pip install uv


# -----------------
# Python package executables
# -----------------
# Use `FOO=$(PYBIN)/foo` to define the path to a package's executable
# Depend on `$(FOO)` to ensure the package is installed,
# but use `$(PYBIN)/foo` to actually run the package's executable
BLACK = $(SITE_PACKAGES)/black
ISORT = $(SITE_PACKAGES)/isort
FLAKE8 = $(SITE_PACKAGES)/flake8
PYTEST = $(SITE_PACKAGES)/pytest
COVERAGE = $(SITE_PACKAGES)/coverage
PYRIGHT = $(SITE_PACKAGES)/pyright
PLAYWRIGHT = $(SITE_PACKAGES)/playwright
$(RUFF) $(PYTEST) $(COVERAGE) $(PYRIGHT) $(PLAYWRIGHT):
	@$(MAKE) install-deps


# -----------------
# Helper packages not defined in `setup.cfg`
# -----------------

TRCLI = $(SITE_PACKAGES)/trcli
$(TRCLI): $(UV)
	@echo "-------- Installing trcli --------"
	. $(PYBIN)/activate && \
	  uv pip install trcli

TWINE = $(SITE_PACKAGES)/twine
$(TWINE): $(UV)
	@echo "-------- Installing twine --------"
	. $(PYBIN)/activate && \
	  uv pip install twine

RSCONNECT = $(SITE_PACKAGES)/rsconnect
# Install the main version of rsconnect till pypi version supports shiny express
$(RSCONNECT): $(UV)
	@echo "-------- Installing rsconnect --------"
	. $(PYBIN)/activate && \
	  uv pip install "rsconnect-python @ git+https://github.com/rstudio/rsconnect-python.git"


# -----------------
# Type stubs
# -----------------

typings/appdirs: $(PYRIGHT)
	@echo "-------- Creating stub for appdirs --------"
	. $(PYBIN)/activate && \
	  pyright --createstub appdirs
typings/folium: $(PYRIGHT)
	@echo "-------- Creating stub for folium --------"
	. $(PYBIN)/activate && \
	  pyright --createstub folium
typings/uvicorn: $(PYRIGHT)
	@echo "-------- Creating stub for uvicorn --------"
	. $(PYBIN)/activate && \
	  pyright --createstub uvicorn
typings/seaborn: $(PYRIGHT)
	@echo "-------- Creating stub for seaborn --------"
	. $(PYBIN)/activate && \
	  pyright --createstub seaborn

typings/matplotlib/__init__.pyi: ## grab type stubs from GitHub
	@echo "-------- Creating stub for matplotlib --------"
	mkdir -p typings
	git clone --depth 1 https://github.com/microsoft/python-type-stubs typings/python-type-stubs
	mv typings/python-type-stubs/stubs/matplotlib typings/
	rm -rf typings/python-type-stubs

pyright-typings: typings/appdirs typings/folium typings/uvicorn typings/seaborn typings/matplotlib/__init__.pyi

# -----------------
# Install
# -----------------
## install the package to the active Python's site-packages
# Note that instead of --force-reinstall, we uninstall and then install, because
# --force-reinstall also reinstalls all deps. And if we also used --no-deps, then the
# deps wouldn't be installed the first time.
install: dist $(PIP) FORCE
	. $(PYBIN)/activate && \
	  pip uninstall -y shiny && \
	  pip install dist/shiny*.whl

install-deps: $(UV) FORCE ## install dependencies
	. $(PYBIN)/activate && \
	  uv pip install -e ".[dev,test]" --refresh

install-ci: $(UV) FORCE ## install dependencies for CI
	. $(PYBIN)/activate && \
	  uv pip install -e ".[dev,test]" --refresh \
	  "htmltools @ git+https://github.com/posit-dev/py-htmltools.git"

# ## If caching is ever used, we could run:
# install-deps: ## install latest dependencies
# 	pip install --editable ".[dev,test]" --upgrade --upgrade-strategy eager

# -----------------
# Clean files
# -----------------
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

# Remove build artifacts
clean-build: FORCE
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

# Remove Python file artifacts
clean-pyc: FORCE
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# Remove test and coverage artifacts
clean-test: FORCE
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -rf typings/


# -----------------
# Check lint, test, and format of code
# -----------------
check: check-format check-lint check-types check-tests  ## check code, style, types, and test (basic CI)
check-fix: format check-lint check-types check-tests ## check and format code, style, types, and test
check-format: check-black check-isort
check-lint: check-flake8
check-types: check-pyright
check-tests: check-pytest

check-flake8: $(FLAKE8) FORCE
	@echo "-------- Checking style with flake8 ---------"
	. $(PYBIN)/activate && \
	  flake8 --show-source .
check-black: $(BLACK) FORCE
	@echo "-------- Checking code with black -----------"
	. $(PYBIN)/activate && \
	  black --check .
check-isort: $(ISORT) FORCE
	@echo "-------- Sorting imports with isort ---------"
	. $(PYBIN)/activate && \
	  isort --check-only --diff .
check-pyright: $(PYRIGHT) pyright-typings
	@echo "-------- Checking types with pyright --------"
	. $(PYBIN)/activate && \
	  pyright
check-pytest: $(PYTEST) FORCE
	@echo "-------- Running tests with pytest ----------"
	. $(PYBIN)/activate && \
	  python tests/pytest/asyncio_prevent.py && \
	  pytest

# Check types with pyright
pyright: check-types
# Check style with flake8
lint: check-lint
test: check-tests ## check tests quickly with the default Python

format: format-black format-isort ## format code with black and isort
format-black: FORCE
	@echo "-------- Formatting code with black --------"
	black .
format-isort: FORCE
	@echo "-------- Sorting imports with isort --------"
	isort .

# -----------------
# Documentation
# -----------------
# Install docs deps; Used in `./docs/Makefile`
install-docs: $(UV) FORCE
	. $(PYBIN)/activate && \
	  uv pip install -e ".[dev,test,doc]" \
	  "htmltools @ git+https://github.com/posit-dev/py-htmltools.git" \
	  "shinylive @ git+https://github.com/posit-dev/py-shinylive.git"

docs: docs-serve FORCE ## docs: build and serve docs in browser

docs-serve: $(PYBIN) FORCE ## docs: build and serve docs in browser
	$(MAKE) docs-quartodoc
	@echo "-------- Previewing docs in browser --------"
	@cd docs && make serve

docs-site: $(PYBIN) FORCE ## docs: build docs site
	$(MAKE) docs-quartodoc
	@echo "-------- Previewing docs in browser --------"
	@cd docs && make site

docs-quartodoc: $(PYBIN) FORCE ## docs: build quartodoc docs
	$(MAKE) install-docs
	@echo "-------- Building docs with quartodoc --------"
	@cd docs && make quartodoc

# -----------------
# JS assets
# -----------------
install-npm: FORCE
	$(if $(shell which npm), @echo -n, $(error Please install node.js and npm first. See https://nodejs.org/en/download/ for instructions.))
js/node_modules: install-npm
	@echo "-------- Installing node_modules -----------"
	@cd js && npm install
js-build: js/node_modules ## Build JS assets
	@echo "-------- Building JS assets ----------------"
	@cd js && npm run build
js-watch: js/node_modules
	@echo "-------- Continuously building JS assets ---"
	@cd js && npm run watch
js-watch-fast: js/node_modules ## Continuously build JS assets (development)
	@echo "-------- Previewing docs in browser --------"
	@cd js && npm run watch-fast
clean-js: FORCE
	@echo "-------- Removing js/node_modules ----------"
	rm -rf js/node_modules


# -----------------
# Testing with playwright
# -----------------

# Default `SUB_FILE` to empty
SUB_FILE:=

install-playwright: $(PLAYWRIGHT) FORCE
	@echo "-------- Installing playwright browsers --------"
	@. $(PYBIN)/activate && \
	  playwright install --with-deps

playwright-shiny: install-playwright $(PYTEST) FORCE ## end-to-end tests with playwright; (SUB_FILE="" within tests/playwright/shiny/)
	. $(PYBIN)/activate && \
	  pytest tests/playwright/shiny/$(SUB_FILE)

playwright-deploys: install-playwright $(RSCONNECT) $(PYTEST) FORCE ## end-to-end tests on deployed apps with playwright; (SUB_FILE="" within tests/playwright/deploys/)
	. $(PYBIN)/activate && \
	  pytest tests/playwright/deploys/$(SUB_FILE)

playwright-examples: install-playwright $(PYTEST) FORCE ## end-to-end tests on all py-shiny examples with playwright; (SUB_FILE="" within tests/playwright/examples/)
	. $(PYBIN)/activate && \
	  pytest tests/playwright/examples/$(SUB_FILE)

playwright-debug: install-playwright $(PYTEST) FORCE ## All end-to-end tests, chrome only, headed; (SUB_FILE="" within tests/playwright/)
	. $(PYBIN)/activate && \
	  pytest -c tests/playwright/playwright-pytest.ini tests/playwright/$(SUB_FILE)

playwright-show-trace: FORCE ## Show trace of failed tests
	npx playwright show-trace test-results/*/trace.zip

# end-to-end tests with playwright and generate junit report
testrail-junit: install-playwright $(TRCLI) $(PYTEST) FORCE
	. $(PYBIN)/activate && \
	  pytest tests/playwright/shiny/$(SUB_FILE) --junitxml=report.xml

coverage: $(PYTEST) $(COVERAGE) FORCE ## check combined code coverage (must run e2e last)
	. $(PYBIN)/activate && \
	  pytest --cov-report term-missing --cov=shiny tests/pytest/ tests/playwright/shiny/$(SUB_FILE) && \
	  coverage html && \
	  $(BROWSER) htmlcov/index.html

# -----------------
# Release
# -----------------
release: $(TWINE) dist FORCE ## package and upload a release
	. $(PYBIN)/activate && \
	  twine upload dist/*

dist: clean $(PYTHON) FORCE ## builds source and wheel package
	. $(PYBIN)/activate && \
	  python setup.py sdist && \
	  python setup.py bdist_wheel
	ls -l dist
