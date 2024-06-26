.PHONY: help Makefile
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

# Use venv from parent
VENV = ../venv
PYBIN = $(VENV)/bin

# Any targets that depend on $(VENV) or $(PYBIN) will cause the venv to be
# created. To use the venv, python scripts should run with the prefix $(PYBIN),
# as in `$(PYBIN)/pip`.
$(VENV):
	python3 -m venv $(VENV)

$(PYBIN): $(VENV)


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

dev-htmltools: $(PYBIN)  ## Install development version of htmltools
	$(PYBIN)/pip install https://github.com/posit-dev/py-htmltools/tarball/main

dev-shinylive: $(PYBIN)  ## Install development version of shinylive
	$(PYBIN)/pip install https://github.com/posit-dev/py-shinylive/tarball/main

deps: $(PYBIN) dev-htmltools dev-shinylive ## Install build dependencies
	$(PYBIN)/pip install pip --upgrade
	$(PYBIN)/pip install ..[doc]

quartodoc: quartodoc_build_core quartodoc_build_express quartodoc_build_test quartodoc_post ## Build quartodocs for express and core

## Build interlinks for API docs
quartodoc_interlinks: $(PYBIN)
	. $(PYBIN)/activate \
	  && quartodoc interlinks

## Build core API docs
quartodoc_build_core: $(PYBIN) quartodoc_interlinks
	$(eval export SHINY_ADD_EXAMPLES=true)
	$(eval export IN_QUARTODOC=true)
	$(eval export SHINY_MODE=core)
	. $(PYBIN)/activate \
	  && echo "::group::quartodoc build core docs" \
	  && quartodoc build --config _quartodoc-core.yml --verbose \
	  && mv objects.json _objects_core.json \
	  && echo "::endgroup::"

## Build express API docs
quartodoc_build_express: $(PYBIN) quartodoc_interlinks
	$(eval export SHINY_ADD_EXAMPLES=true)
	$(eval export IN_QUARTODOC=true)
	$(eval export SHINY_MODE=express)
	. $(PYBIN)/activate \
	  && echo "::group::quartodoc build express docs" \
	  && quartodoc build --config _quartodoc-express.yml --verbose \
	  && mv objects.json _objects_express.json \
	  && echo "::endgroup::"

## Build test API docs
quartodoc_build_test: $(PYBIN) quartodoc_interlinks
	. $(PYBIN)/activate \
	  && echo "::group::quartodoc build testing docs" \
	  && quartodoc build --config _quartodoc-testing.yml --verbose \
	  && mv objects.json _objects_test.json \
	  && echo "::endgroup::"

## Clean up after quartodoc build
quartodoc_post: $(PYBIN)
	. $(PYBIN)/activate \
	  && python _combine_objects_json.py

site:  ## Build website
	. $(PYBIN)/activate \
	  && quarto render

serve:  ## Build website and serve
	. $(PYBIN)/activate \
	  && quarto preview --port 8080

clean:  ## Clean build artifacts
	rm -rf _inv api _site .quarto
