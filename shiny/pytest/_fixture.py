from __future__ import annotations

from pathlib import Path, PurePath
from typing import Literal, Union

import pytest

from .._docstring import no_example
from ..run._run import shiny_app_gen

__all__ = (
    "create_app_fixture",
    "ScopeName",
)


ScopeName = Literal["session", "package", "module", "class", "function"]
"""
Pytest fixture scopes

Fixtures are created when first requested by a test, and are destroyed based on their scope:

* `function`: the default scope, the fixture is destroyed at the end of the test.
* `class`: the fixture is destroyed during teardown of the last test in the class.
* `module`: the fixture is destroyed during teardown of the last test in the module.
* `package`: the fixture is destroyed during teardown of the last test in the package.
* `session`: the fixture is destroyed at the end of the test session.

**Note:** Pytest only caches one instance of a fixture at a time, which means that when using a parametrized fixture, pytest may invoke a fixture more than once in the given scope.

Documentation taken from [https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#fixture-scopes](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#fixture-scopes)
"""


@no_example()
def create_app_fixture(
    app: Union[PurePath, str],
    scope: ScopeName = "module",
):
    """
    Create a fixture for a local Shiny app directory.

    Creates a fixture for a local Shiny app that is not contained within the same folder. This fixture is used to start the Shiny app process and return the local URL of the app.

    If the app path is located in the same directory as the test file, then `create_app_fixture()` can be skipped and `local_app` test fixture can be used instead.

    Parameters
    ----------
    app
        The path to the Shiny app file.

        If `app` is a `Path` or `PurePath` instance and `Path(app).is_file()` returns
        `True`, then this value will be used directly. Note, `app`'s file path will be
        checked from where corresponding `pytest` test is collected, not necessarily
        where `create_app_fixture()` is called.

        Otherwise, all `app` paths will be considered to be relative paths from where
        the test function was collected.

        To be sure that your `app` path is always relative, supply a `str` value.
    scope
        The scope of the fixture.

    Returns
    -------
    fixture_func
        The fixture function.

    Examples
    --------
    ```python
    from playwright.sync_api import Page

    from shiny.playwright import controller
    from shiny.pytest import create_app_fixture
    from shiny.run import ShinyAppProc

    # The variable name `app` MUST match the parameter name in the test function
    app = create_app_fixture("relative/path/to/app.py")


    def test_app_code(page: Page, app: ShinyAppProc):

        page.goto(app.url)
        # Add test code here
        ...
    ```
    """

    @pytest.fixture(scope=scope)
    def fixture_func(request: pytest.FixtureRequest):
        app_purepath_exists = isinstance(app, PurePath) and Path(app).is_file()
        app_path = app if app_purepath_exists else request.path.parent / app
        sa_gen = shiny_app_gen(app_path)
        yield next(sa_gen)

    return fixture_func
