Shiny for Python
================

This repository contains an implementation of Shiny for Python. It works with Python 3.7 and above.

## Usage

First clone the [py-htmltools](https://github.com/rstudio/py-htmltools) repository and install the package:

```sh
git clone https://github.com/rstudio/py-htmltools.git
cd py-htmltools
pip install -r requirements.txt
pip install -e .
```

(Note: `pip install -e .` will make the package load from the dev directory on disk; then whenever you update the code, it will immediately be available to Python without having to reinstall. If you want to install these packages the normal way, use `make install` instead.)

Next, clone this repository and install it:

```sh
git clone https://github.com/rstudio/py-shiny.git
cd py-shiny
pip install -r requirements.txt
pip install -e .
```

To run an example app:

```sh
shiny run examples/inputs/
```

Then visit the app by pointing a web browser to http://localhost:8000/.

## Development

If you want to do development, run:

```sh
pip install -r requirements-dev.txt
```

Additionally, you can install pre-commit hooks which will automatically reformat and lint the code when you make a commit:

```sh
pre-commit install

# To disable:
# pre-commit uninstall
```
