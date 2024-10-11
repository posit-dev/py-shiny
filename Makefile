# https://www.gnu.org/software/make/manual/make.html#Phony-Targets
# Prerequisites of .PHONY are always interpreted as literal target names, never as patterns (even if they contain ‘%’ characters).
# # .PHONY: help clean% check% format% docs% lint test pyright playwright% install% coverage release js-*
# Using `FORCE` as prerequisite to _force_ the target to always run; https://www.gnu.org/software/make/manual/make.html#index-FORCE
FORCE: ;

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

help: FORCE
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

# Remove build artifacts
clean-build: FORCE
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

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

typings/appdirs:
	@echo "Creating appdirs stubs"
	pyright --createstub appdirs
typings/folium:
	@echo "Creating folium stubs"
	pyright --createstub folium
typings/uvicorn:
	@echo "Creating uvicorn stubs"
	pyright --createstub uvicorn
typings/seaborn:
	@echo "Creating seaborn stubs"
	pyright --createstub seaborn
typings/matplotlib/__init__.pyi:
	@echo "Creating matplotlib stubs"
	mkdir -p typings
	git clone --depth 1 https://github.com/microsoft/python-type-stubs typings/python-type-stubs
	mv typings/python-type-stubs/stubs/matplotlib typings/
	rm -rf typings/python-type-stubs

pyright-typings: typings/appdirs typings/folium typings/uvicorn typings/seaborn typings/matplotlib/__init__.pyi

check: check-format check-lint check-types check-tests  ## check code, style, types, and test (basic CI)
check-fix: format check-lint check-types check-tests ## check and format code, style, types, and test
check-format: check-black check-isort
check-lint: check-flake8
check-types: check-pyright
check-tests: check-pytest

check-flake8: FORCE
	@echo "-------- Checking style with flake8 ---------"
	flake8 --show-source .
check-black: FORCE
	@echo "-------- Checking code with black -----------"
	black --check .
check-isort: FORCE
	@echo "-------- Sorting imports with isort ---------"
	isort --check-only --diff .
check-pyright: pyright-typings
	@echo "-------- Checking types with pyright --------"
	pyright
check-pytest: FORCE
	@echo "-------- Running tests with pytest ----------"
	python tests/pytest/asyncio_prevent.py
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

docs: FORCE ## docs: build docs with quartodoc
	@echo "-------- Building docs with quartodoc ------"
	@cd docs && make quartodoc

docs-preview: FORCE ## docs: preview docs in browser
	@echo "-------- Previewing docs in browser --------"
	@cd docs && make serve
docs-quartodoc: FORCE
	@echo "-------- Making quartodoc docs --------"
	@cd docs && make quartodoc


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

# Default `SUB_FILE` to empty
SUB_FILE:=
PYTEST_BROWSERS:= --browser webkit --browser firefox --browser chromium
PYTEST_DEPLOYS_BROWSERS:= --browser chromium


# Full test path to playwright tests
TEST_FILE:=tests/playwright/$(SUB_FILE)
# Default `make` values that shouldn't be directly used; (Use `TEST_FILE` instead!)
DEPLOYS_TEST_FILE:=tests/playwright/deploys$(SUB_FILE)
SHINY_TEST_FILE:=tests/playwright/shiny/$(SUB_FILE)
EXAMPLES_TEST_FILE:=tests/playwright/examples/$(SUB_FILE)

install-playwright: FORCE
	playwright install --with-deps

install-rsconnect: FORCE
	pip install git+https://github.com/rstudio/rsconnect-python.git#egg=rsconnect-python


# All end-to-end tests with playwright
playwright: install-playwright ## All end-to-end tests with playwright; (TEST_FILE="" from root of repo)
	pytest $(TEST_FILE) $(PYTEST_BROWSERS)

playwright-debug: install-playwright ## All end-to-end tests, chrome only, headed; (TEST_FILE="" from root of repo)
	pytest -c tests/playwright/playwright-pytest.ini $(TEST_FILE)

playwright-show-trace: ## Show trace of failed tests
	npx playwright show-trace test-results/*/trace.zip

# end-to-end tests with playwright; (SUB_FILE="" within tests/playwright/shiny/)
playwright-shiny: FORCE
	$(MAKE) playwright TEST_FILE="$(SHINY_TEST_FILE)"

# end-to-end tests on deployed apps with playwright; (SUB_FILE="" within tests/playwright/deploys/)
playwright-deploys: FORCE
	$(MAKE) playwright PYTEST_BROWSERS="$(PYTEST_DEPLOYS_BROWSERS)" TEST_FILE="$(DEPLOYS_TEST_FILE)"

# end-to-end tests on all py-shiny examples with playwright; (SUB_FILE="" within tests/playwright/examples/)
playwright-examples: FORCE
	$(MAKE) playwright TEST_FILE="$(EXAMPLES_TEST_FILE)"

coverage: FORCE ## check combined code coverage (must run e2e last)
	pytest --cov-report term-missing --cov=shiny tests/pytest/ $(SHINY_TEST_FILE) $(PYTEST_BROWSERS)
	coverage html
	$(BROWSER) htmlcov/index.html

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	pip install build
	python -m build --sdist
	python -m build --wheel
	ls -l dist


## install the package to the active Python's site-packages
# Note that instead of --force-reinstall, we uninstall and then install, because
# --force-reinstall also reinstalls all deps. And if we also used --no-deps, then the
# deps wouldn't be installed the first time.
install: dist
	pip uninstall -y shiny
	python -m pip install dist/shiny*.whl
ci-install-wheel: dist FORCE
	# `uv` version of `make install`
	uv pip uninstall shiny
	uv pip install dist/shiny*.whl

install-deps: FORCE ## install dependencies
	pip install -e ".[dev,test]" --upgrade
ci-install-deps: FORCE
	uv pip install -e ".[dev,test]"

install-docs: FORCE
	pip install -e ".[dev,test,doc]"
	pip install https://github.com/posit-dev/py-shinylive/tarball/main
ci-install-docs: FORCE
	uv pip install -e ".[dev,test,doc]" \
		"shinylive @ git+https://github.com/posit-dev/py-shinylive.git"

ci-install-rsconnect: FORCE
	uv pip install "rsconnect-python @ git+https://github.com/rstudio/rsconnect-python.git"


# This is just to check if mypy can run for other users.
# Not added to `make check` or `make check-fix` as all lint errors are supporessed (as we use pyright).
ci-check-mypy-can-run: FORCE
	@echo "-------- Checking types with mypy -----------"
	uv pip install mypy
	mypy shiny


# ## If caching is ever used, we could run:
# install-deps: FORCE ## install latest dependencies
# 	pip install --editable ".[dev,test]" --upgrade --upgrade-strategy eager

upgrade-html-deps: FORCE ## Upgrade Shiny's HTMLDependencies
	@if ! Rscript -e "q()"; then \
	  echo "Error: Upgrading HTML dependencies requires R, but R is not installed or not in your PATH. Please install R and try again."; \
	  exit 1; \
	fi
	@scripts/htmlDependencies.R

narwhals-install-shiny: FORCE
	@echo "-------- Install py-shiny ----------"
	$(MAKE) ci-install-deps
narwhals-test-integration: FORCE
	@echo "-------- Running py-shiny format, lint, typing, and unit tests ----------"
	$(MAKE) check
	@echo "-------- Running py-shiny playwright tests ----------"
	$(MAKE) playwright TEST_FILE="tests/playwright/shiny/components/data_frame" PYTEST_BROWSERS="--browser chromium"
