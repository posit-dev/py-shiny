Shiny for Python
================


[![Release](https://img.shields.io/github/v/release/rstudio/py-shiny)](https://img.shields.io/github/v/release/rstudio/py-shiny)
[![Build status](https://img.shields.io/github/workflow/status/rstudio/py-shiny/Run%20tests)](https://img.shields.io/github/workflow/status/rstudio/py-shiny/Run%20tests)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/deptry)](https://pypi.org/project/deptry/)
[![License](https://img.shields.io/github/license/rstudio/py-shiny)](https://img.shields.io/github/license/rstudio/py-shiny)


## What is Shiny?

See the [Shiny for Python website](https://shiny.rstudio.com/py/).

## Installation

To install the latest release from PyPI:

```sh
pip install shiny
```

To install the latest development version from this repository:

```sh
pip install https://github.com/rstudio/py-shiny/tarball/main
```

More detailed installation instructions, including the use of `conda`, are [also available](https://shiny.rstudio.com/py/docs/install.html).

## Development

If you want to do development on Shiny for Python:

```sh
pip install -r requirements-dev.txt
```

Additionally, you can install pre-commit hooks which will automatically reformat and lint the code when you make a commit:

```sh
pre-commit install

# To disable:
# pre-commit uninstall
```
