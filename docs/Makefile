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
	$(PYBIN)/pip install https://github.com/rstudio/py-htmltools/tarball/main

deps: $(PYBIN)  ## Install build dependencies
	$(PYBIN)/pip install pip --upgrade
	$(PYBIN)/pip install -e ..[doc]

quartodoc: $(PYBIN) ## Build qmd files for API docs
	$(eval export SHINY_ADD_EXAMPLES=true)
	$(eval export IN_QUARTODOC=true)
	. $(PYBIN)/activate \
	  && quartodoc interlinks \
	  && quartodoc build --config _quartodoc.yml --verbose

site:  ## Build website
	. $(PYBIN)/activate \
	  && quarto render

serve:  ## Build website and serve
	. $(PYBIN)/activate \
	  && quarto preview --port 8080

clean:  ## Clean build artifacts
	rm -rf _inv api _site .quarto
