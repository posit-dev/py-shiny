Shiny for Python
================

This repository contains an implementation of Shiny for Python.

## Usage

First, clone this repository. Then run:

```sh
pip install -r requirements.txt
make install
```

To run an example app:

```sh
python3 myapp/app.py
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
