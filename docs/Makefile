# Using `FORCE` as prerequisite to _force_ the target to always run; https://www.gnu.org/software/make/manual/make.html#index-FORCE
FORCE: ;

.PHONY: Makefile
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

deps: FORCE ## Install build dependencies
	cd .. && $(MAKE) install-docs

quartodoc: quartodoc_build_core quartodoc_build_express quartodoc_build_test quartodoc_post ## Build quartodocs for express, core, and testing

## Build interlinks for API docs
quartodoc_interlinks: FORCE
	quartodoc interlinks

## Build core API docs
quartodoc_build_core: quartodoc_interlinks FORCE
	$(eval export SHINY_ADD_EXAMPLES=true)
	$(eval export IN_QUARTODOC=true)
	$(eval export SHINY_MODE=core)
	@echo "::group::quartodoc build core docs"
	quartodoc build --config _quartodoc-core.yml --verbose \
	  && mv objects.json _objects_core.json
	@echo "::endgroup::"

## Build express API docs
quartodoc_build_express: quartodoc_interlinks FORCE
	$(eval export SHINY_ADD_EXAMPLES=true)
	$(eval export IN_QUARTODOC=true)
	$(eval export SHINY_MODE=express)
	@echo "::group::quartodoc build express docs"
	quartodoc build --config _quartodoc-express.yml --verbose \
	  && mv objects.json _objects_express.json
	@echo "::endgroup::"

## Build test API docs
quartodoc_build_test: quartodoc_interlinks FORCE
	$(eval export SHINY_ADD_EXAMPLES=true)
	$(eval export IN_QUARTODOC=true)
	$(eval export SHINY_MODE=express)
	@echo "::group::quartodoc build testing docs"
	quartodoc build --config _quartodoc-testing.yml --verbose \
	  && mv objects.json _objects_test.json
	@echo "::endgroup::"

## Clean up after quartodoc build
quartodoc_post: FORCE
	python _combine_objects_json.py

site: FORCE  ## Build website (quarto render)
	quarto render

serve: FORCE  ## Build website and serve (quarto preview)
	quarto preview --port 8080

clean: FORCE  ## Clean build artifacts
	rm -rf _inv api _site .quarto
