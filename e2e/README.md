# End-to-end tests

This directory contains end-to-end tests for Shiny for Python. Each subdirectory
contains one or more Pytest files (`test_*.py`) containing
[Playwright](https://playwright.dev/python/) assertions, and optionally, a single app
(`app.py`) that the assertions test against. (The app is optional, because the tests may
also be for apps in the `examples/` directory.)

The following commands can be run from the repo root:

```sh
# Run all e2e tests
make e2e
# Another way to run all e2e tests
tox

# Run just the tests in e2e/async/
tox e2e/async

# Run just the tests in e2e/async/, in headed mode
tox -- --headed e2e/async
```

## Shiny app fixtures

Playwright for Python launches and controls (headless or headful) browsers, but does not
know how to start/stop Shiny app processes. These are handled by fixtures in
`conftest.py`.

The fixtures wait until the app has finished loading and is responding to requests,
before passing control back to Pytest and letting the test begin. The scope of each
fixture is `module`; that is, the local app will be started and shutdown once regardless
of how many test functions exist in this module. (We can easily make this customizable
in the future if necessary.)

### Testing a local `app.py`

The `local_app: ShinyAppProc` fixture launches the `app.py` in the current directory
(relative to the `test_*.py` file).

```python
# pyright: reportUnknownMemberType=false

import re
from playwright.sync_api import Page, expect
from conftest import ShinyAppProc


def test_airmass(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
```

### Testing an app from `../examples`

Testing an example app is slightly more complicated. At the test module level, create a
fixture with the help of `conftest.create_example_fixture`, and use it from test funcs.

```python
# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

import re

from playwright.sync_api import Page, expect

from conftest import ShinyAppProc, create_example_fixture

airmass_app = create_example_fixture("airmass")


def test_airmass(page: Page, airmass_app: ShinyAppProc):
    page.goto(airmass_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
```
