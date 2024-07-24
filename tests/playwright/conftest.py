# This file is necessary for pytest to find relative module files
# such as examples/example_apps.py

from __future__ import annotations

from pathlib import PurePath
from typing import Generator

import pytest
from playwright.sync_api import (
    BrowserContext,
    ConsoleMessage,
    JSHandle,
    Page,
    SourceLocation,
)

from shiny._typing_extensions import TypedDict
from shiny.pytest import ScopeName as ScopeName
from shiny.pytest import create_app_fixture

__all__ = (
    "create_doc_example_fixture",
    "create_example_fixture",
    "create_doc_example_core_fixture",
    "create_doc_example_express_fixture",
)


here = PurePath(__file__).parent
here_root = here.parent.parent


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


class ConsoleMessageInfo(TypedDict):
    type: str
    text: str
    location: SourceLocation
    args: list[JSHandle]


@pytest.fixture(scope="function")
# By going to `about:blank`, we _reset_ the page to a known state before each test.
# It is not perfect, but it is faster than making a new page for each test.
# This must be done before each test
def page(
    request: pytest.FixtureRequest,
    session_page: Page,
) -> Generator[Page, None, None]:
    """
    Reset the given page to a known state before each test.

    The page is built on the session_page, which is maintained over the full session.
    The page will visit "about:blank" to reset between apps.
    The default viewport size is set to 1920 x 1080 (1080p) for each test function.

    Parameters:
        session_page (Page): The page to reset before each test.
    """
    session_page.goto("about:blank")
    # Reset screen size to 1080p
    session_page.set_viewport_size({"width": 1920, "height": 1080})

    console_msgs: list[ConsoleMessageInfo] = []

    def on_console_msg(msg: ConsoleMessage) -> None:
        # Do not report missing favicon errors
        if msg.location["url"].endswith("favicon.ico"):
            return
        if msg.type == "warning" and msg.text.startswith("DEPRECATED:"):
            return
        # console_msgs.append(msg.text)
        console_msgs.append(
            {
                "type": msg.type,
                "text": msg.text,
                "location": msg.location,
                "args": msg.args,
            }
        )

    session_page.on("console", on_console_msg)

    yield session_page

    session_page.remove_listener("console", on_console_msg)

    if request.session.testsfailed:
        if len(console_msgs) > 0:
            print("+++++++++ Browser console log ++++++++")
            for msg in console_msgs:
                print(msg)
            print("+++++++++ / Browser console log ++++++++")
        else:
            print("No browser console messages captured.")


def create_example_fixture(
    example_name: str,
    example_file: str = "app.py",
    scope: ScopeName = "module",
):
    """Used to create app fixtures from apps in py-shiny/examples"""
    return create_app_fixture(
        here_root / "examples" / example_name / example_file, scope
    )


def create_doc_example_fixture(
    example_name: str,
    example_file: str = "app.py",
    scope: ScopeName = "module",
):
    """Used to create app fixtures from apps in py-shiny/shiny/api-examples"""
    return create_app_fixture(
        here_root / "shiny/api-examples" / example_name / example_file, scope
    )


def create_doc_example_core_fixture(
    example_name: str,
    scope: ScopeName = "module",
):
    """Used to create app fixtures from ``app-core.py`` example apps in py-shiny/shiny/api-examples"""
    return create_doc_example_fixture(example_name, "app-core.py", scope)


def create_doc_example_express_fixture(
    example_name: str,
    scope: ScopeName = "module",
):
    """Used to create app fixtures from ``app-express.py`` example apps in py-shiny/shiny/api-examples"""
    return create_doc_example_fixture(example_name, "app-express.py", scope)
