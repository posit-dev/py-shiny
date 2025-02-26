# Shiny for Python

[![PyPI Latest Release](https://img.shields.io/pypi/v/shiny.svg)](https://pypi.org/project/shiny/)
[![Build status](https://img.shields.io/github/actions/workflow/status/posit-dev/py-shiny/pytest.yaml?branch=main)](https://img.shields.io/github/actions/workflow/status/posit-dev/py-shiny/pytest.yaml?branch=main)
[![Conda Latest Release](https://anaconda.org/conda-forge/shiny/badges/version.svg)](https://anaconda.org/conda-forge/shiny)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/shiny)](https://pypi.org/project/shiny/)
[![License](https://img.shields.io/github/license/posit-dev/py-shiny)](https://github.com/posit-dev/py-shiny/blob/main/LICENSE)

Shiny for Python is the best way to build fast, beautiful web applications in Python. You can build quickly with Shiny and create simple interactive visualizations and prototype applications in an afternoon. But unlike other frameworks targeted at data scientists, Shiny does not limit your app's growth. Shiny remains extensible enough to power large, mission-critical applications.

To learn more about Shiny see the [Shiny for Python website](https://shiny.posit.co/py/). If you're new to the framework we recommend these resources:

- How [Shiny is different](https://posit.co/blog/why-shiny-for-python/) from Dash and Streamlit.

- How [reactive programming](https://shiny.posit.co/py/docs/reactive-programming.html) can help you build better applications.

- How to [use modules](https://shiny.posit.co/py/docs/workflow-modules.html) to efficiently develop large applications.

- Hosting applications for free on [shinyapps.io](https://shiny.posit.co/py/docs/deploy.html#deploy-to-shinyapps.io-cloud-hosting), [Hugging Face](https://shiny.posit.co/blog/posts/shiny-on-hugging-face/), or [Shinylive](https://shiny.posit.co/py/docs/shinylive.html).

## Join the conversation

If you have questions about Shiny for Python, or want to help us decide what to work on next, [join us on Discord](https://discord.gg/yMGCamUMnS).

## Getting started

To get started with shiny follow the [installation instructions](https://shiny.posit.co/py/docs/install-create-run.html) or just install it from pip.

```sh
pip install shiny
```

To install the latest development version:

```sh
# First install htmltools, then shiny
pip install git+https://github.com/posit-dev/py-htmltools.git#egg=htmltools
pip install git+https://github.com/posit-dev/py-shiny.git#egg=shiny
```

You can create and run your first application with `shiny create`, the CLI will ask you which template you would like to use. You can either run the app with the Shiny extension, or call `shiny run app.py --reload --launch-browser`.

## Development

* Shinylive built from the `main` branch: https://posit-dev.github.io/py-shiny/shinylive/py/examples/
* API documentation for the `main` branch:
    * https://posit-dev.github.io/py-shiny/docs/api/express/
    * https://posit-dev.github.io/py-shiny/docs/api/core/

If you are working from a fork you may not have the git tags from the original repo.
Git tags are required for the install to succeed. To add tags to your own fork:

```sh
git remote add upstream https://github.com/posit-dev/py-shiny.git
git fetch --tags upstream
```

Then install:

```sh
pip install -e ".[dev,test,doc]"
```

Additionally, you can install pre-commit hooks which will automatically reformat and lint the code when you make a commit:

```sh
pre-commit install

# To disable:
# pre-commit uninstall
```

Tests should now pass:

```sh
make check
# To apply formatting fixes instead of erroring:
# make check-fix
```

Or get a full list of helpers with just:

```sh
make
```

Typically, when developing new features for Shiny, you'll want to try them out in an application.
In a **separate** application directory, use can use `-e` to reference your local checkout of `py-shiny`:

```sh
# Rather than
#   pip install shiny
# run:
pip install -e ../py-shiny --config-settings editable_mode=compat
```

See the [docs README](docs/README.md) for instructions on building the documentation locally.
