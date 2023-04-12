Shiny for Python
================

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
pip install -e ".[dev,test]"
```

Additionally, you can install pre-commit hooks which will automatically reformat and lint the code when you make a commit:

```sh
pre-commit install

# To disable:
# pre-commit uninstall
```
