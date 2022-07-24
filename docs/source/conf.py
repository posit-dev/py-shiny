# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

from sphinx.application import Sphinx

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../sphinxext"))

# -- Project information -----------------------------------------------------

project = "Shiny"
copyright = "2022, RStudio"
author = "RStudio"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "pyshinyapp",  # custom shiny extention for embedded apps in docs
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# https://sphinx-book-theme.readthedocs.io/en/latest/tutorials/get-started.html
html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/rstudio/py-shiny",
    "use_repository_button": True,
}

html_title = "for Python"

html_logo = "images/shiny-logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Shiny specific options --------------------------------------------------

# Tell @shiny._docstring.add_example() to actually add examples to the docstrings.
os.environ["SHINY_ADD_EXAMPLES"] = "true"


# WARNING: if you're thinking about adding subclasses of docutils.nodes.Element here,
# don't! You'll get unhelpful pickling errors. https://github.com/sphinx-doc/sphinx/pull/6754
# Instead, add them to the docs/source/sphinxext/ directory and add the name to the
# extensions list above (as done for pyshinyapp).


def setup(app: Sphinx) -> None:
    app.add_js_file("js/fix-logo-link.js")
    app.add_js_file("js/disable-keypress.js")
