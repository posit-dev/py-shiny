Shiny for Python API docs
=========================

This directory contains files to generate Shiny for Python API documentation, using [Quartodoc](https://machow.github.io/quartodoc/get-started/overview.html) and [Quarto](https://quarto.org/).

## Building the docs

To build the docs, first install the Python dependencies and Quarto extensions:

```bash
# Install build dependencies
make deps
```

After those dependencies are installed, build the .qmd files for Shiny, using quartodoc. This will go in the `api/` directory:

```bash
make quartodoc
```

Then build the web site using Quarto:

```bash
make site
```

Alternatively, running `make serve` will build the docs, and serve them locally, and watch for changes to the .qmd files:

```bash
make serve
```
