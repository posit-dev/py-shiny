from __future__ import annotations

from pathlib import PurePath
from typing import Generator

import pytest

from ._conftest import ShinyAppProc
from ._playwright import BrowserContext, Page
from .fixture import local_app_fixture_gen


# Make a single page fixture that can be used by all tests
@pytest.fixture(scope="session")
# By using a single page, the browser is only launched once and all tests run in the same tab / page.
def session_page(browser: BrowserContext) -> Page:
    """
    Create a new page within the given browser context.

    Parameters:
        browser (BrowserContext): The browser context in which to create the new page.

    Returns:
        Page: The newly created page.

    """
    return browser.new_page()


@pytest.fixture(scope="function")
# By going to `about:blank`, we _reset_ the page to a known state before each test.
# It is not perfect, but it is faster than making a new page for each test.
# This must be done before each test
def page(session_page: Page) -> Page:
    """
    Reset the given page to a known state before each test.
    The page is built on the session_page, which is maintained over the full session.
    The page will visit "about:blank" to reset between apps.
    The default viewport size is set to 1920 x 1080 (1080p) for each test function.

    Parameters:
        session_page (Page): The page to reset.
    """
    session_page.goto("about:blank")
    # Reset screen size to 1080p
    session_page.set_viewport_size({"width": 1920, "height": 1080})
    return session_page


@pytest.fixture(scope="module")
def local_app(request: pytest.FixtureRequest) -> Generator[ShinyAppProc, None, None]:
    """
    Create a local Shiny app for testing.

    Parameters:
        request (pytest.FixtureRequest): The request object for the fixture.
    """
    app_gen = local_app_fixture_gen(PurePath(request.path).parent / "app.py")
    yield next(app_gen)
