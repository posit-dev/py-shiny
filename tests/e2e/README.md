# End-to-end tests

This directory contains end-to-end (i.e. browser based) tests for Shiny for Python.

The Python files directly in this subdirectory are for Pytest fixtures and helper code
to make test writing easier. (Eventually this logic may move to the `shiny` package
itself or its own dedicated package, so that Shiny app authors can set up their own e2e
tests against their apps.)

The actual tests are in subdirectories. Each subdirectory contains one or more Pytest
files (`test_*.py`) containing [Playwright](https://playwright.dev/python/) assertions,
and optionally, a single app (`app.py`) that the assertions test against. (The app is
optional, because the tests may also be for apps in the `../examples` or `../shiny/api-examples` directory.)

## Running tests

The following commands can be run from the repo root:

```sh
# Run all e2e tests
make e2e

# Run just the tests in e2e/async/
make e2e FILE=e2e/async

# Run just the tests in e2e/async/, in headed mode
make e2e FILE="--headed e2e/async"
```

## Shiny app fixtures

Playwright for Python launches and controls (headless or headful) browsers, but does not
know how to start/stop Shiny app processes. Instead, we have our own [Pytest
fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html) for
Shiny app process management.

### Testing a local `app.py`

The `local_app: ShinyAppProc` fixture launches the `app.py` in the current directory
as the calling `test_*.py` file.

```python

import re
from playwright.sync_api import Page, expect
from conftest import ShinyAppProc


def test_airmass(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
```

### Testing an app from `../examples`

It's also possible to test apps that live in the `../examples` directory: at the test
module level, create a fixture with the help of `conftest.create_example_fixture`, and
use it from test funcs.

```python
import re

from playwright.sync_api import Page, expect

from conftest import ShinyAppProc, create_example_fixture

airmass_app = create_example_fixture("airmass")


def test_airmass(page: Page, airmass_app: ShinyAppProc):
    page.goto(airmass_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
```
