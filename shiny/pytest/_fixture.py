from __future__ import annotations

from pathlib import Path, PurePath
from typing import Literal

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
    app: PurePath | str | list[PurePath | str],
    scope: ScopeName = "module",
    timeout_secs: float = 30,
):
    """
    Create a fixture for a local Shiny app directory.

    Creates a fixture for a local Shiny app that is not contained within the same
    folder. This fixture is used to start the Shiny app process and return the local URL
    of the app.

    If the app path is located in the same directory as the test file, then
    `create_app_fixture()` can be skipped and `local_app` test fixture can be used
    instead.

    Parameters
    ----------
    app
        The path (or a list of paths) to the Shiny app file.

        If `app` is a `Path` or `PurePath` instance and `Path(app).is_file()` returns
        `True`, then this value will be used directly. Note, `app`'s file path will be
        checked from where corresponding `pytest` test is collected, not necessarily
        where `create_app_fixture()` is called.

        Otherwise, all `app` paths will be considered to be relative paths from where
        the test function was collected.

        To be sure that your `app` path is always relative, supply a `str` value.

        If `app` is a list of path values, then the fixture will be parametrized and each test
        will be run for each path in the list.
    scope
        The scope of the fixture. The default is `module`, which means that the fixture
        will be created once per module. See [Pytest fixture
        scopes](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes)
        for more details.
    timeout_secs
        The maximum number of seconds to wait for the app to become ready.

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

    ```python
    from playwright.sync_api import Page

    from shiny.playwright import controller
    from shiny.pytest import create_app_fixture
    from shiny.run import ShinyAppProc

    # The variable name `app` MUST match the parameter name in the test function
    # The tests below will run for each path provided
    app = create_app_fixture(["relative/path/to/first/app.py", "relative/path/to/second/app.py"])

    def test_app_code(page: Page, app: ShinyAppProc):

        page.goto(app.url)
        # Add test code here
        ...

    def test_more_app_code(page: Page, app: ShinyAppProc):

        page.goto(app.url)
        # Add test code here
        ...
    ```
    """

    def get_app_path(request: pytest.FixtureRequest, app: PurePath | str):
        app_purepath_exists = isinstance(app, PurePath) and Path(app).is_file()
        app_path = app if app_purepath_exists else request.path.parent / app
        return app_path

    if isinstance(app, list):

        # Multiple app values provided
        # Will display the app value as a parameter in the logs
        @pytest.fixture(scope=scope, params=app)
        def fixture_func(request: pytest.FixtureRequest):
            app_path = get_app_path(request, request.param)
            sa_gen = shiny_app_gen(app_path, timeout_secs=timeout_secs)
            yield next(sa_gen)

    else:
        # Single app value provided
        # No indication of the app value in the logs
        @pytest.fixture(scope=scope)
        def fixture_func(request: pytest.FixtureRequest):
            app_path = get_app_path(request, app)
            sa_gen = shiny_app_gen(app_path, timeout_secs=timeout_secs)
            yield next(sa_gen)

    return fixture_func
