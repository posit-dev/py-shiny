# This file is necessary for pytest to find relative module files
# such as examples/example_apps.py
from __future__ import annotations

import logging
import os
import typing
from inspect import signature
from pathlib import PurePath

import pytest
from playwright.sync_api import BrowserContext, BrowserType, Page, Response

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


# Attribute set on a Page once it can no longer navigate (e.g. its WebKit web
# process crashed). The `page` fixture replaces a page marked this way.
_NAVIGATION_WEDGED_ATTR = "_shiny_navigation_wedged"


def _new_session_page(browser: BrowserContext) -> Page:
    """
    Create a shared page whose `goto()` verifies the navigation committed.
    Parameters:
        browser (BrowserContext): The browser context in which to create the new page.
    Returns:
        Page: The newly created page.
    """
    page = browser.new_page()
    page.on("crash", lambda page: setattr(page, _NAVIGATION_WEDGED_ATTR, True))
    original_goto = page.goto

    def goto_and_verify_commit(url: str, **kwargs: typing.Any) -> Response | None:
        # WebKit occasionally swallows a navigation issued right after the
        # `about:blank` reset performed by the function-scoped `page` fixture:
        # `goto()` returns normally but the page never leaves `about:blank`,
        # so every subsequent locator wait times out. When that happens,
        # retry the navigation once. If the retry is also swallowed, the page
        # is wedged and no future navigation will commit either, so mark it
        # for replacement and fail fast; a flaky rerun then gets a fresh page
        # instead of timing out on the same broken one.
        response = original_goto(url, **kwargs)
        if url != "about:blank" and page.url == "about:blank":
            logging.warning(
                "Navigation to %s did not commit (page still on about:blank); retrying one time",
                url,
            )
            response = original_goto(url, **kwargs)
            if page.url == "about:blank":
                setattr(page, _NAVIGATION_WEDGED_ATTR, True)
                raise RuntimeError(
                    f"Navigation to {url} did not commit after retry; "
                    "the shared page will be replaced on the next test attempt"
                )
        return response

    page.goto = goto_and_verify_commit  # pyright: ignore[reportAttributeAccessIssue]
    return page


@pytest.fixture(scope="session")
def _session_page_holder() -> list[Page]:
    """
    Session-scoped holder for the shared page.
    By using a single page, the browser is only launched once and all tests run
    in the same tab / page. The holder (rather than a plain session-scoped page
    fixture) lets the `page` fixture replace the shared page if it becomes
    unusable mid-session.
    """
    return []


@pytest.fixture(scope="function")
# By going to `about:blank`, we _reset_ the page to a known state before each test.
# It is not perfect, but it is faster than making a new page for each test.
# This must be done before each test
def page(browser: BrowserContext, _session_page_holder: list[Page]) -> Page:
    """
    Reset the shared page to a known state before each test.
    The page is maintained over the full session and reset by visiting
    "about:blank" between apps. If the page has become unusable (crashed or
    wedged so navigations no longer commit), it is replaced with a new page.
    The default viewport size is set to 1920 x 1080 (1080p) for each test function.
    Parameters:
        browser (BrowserContext): The browser context used to create replacement pages.
        _session_page_holder (list[Page]): Holder for the shared page.
    """
    session_page = _session_page_holder[0] if _session_page_holder else None
    if session_page is not None:
        if session_page.is_closed() or getattr(
            session_page, _NAVIGATION_WEDGED_ATTR, False
        ):
            logging.warning("Shared page is unusable; replacing it with a new page")
            if not session_page.is_closed():
                session_page.close()
            session_page = None
        else:
            try:
                session_page.goto("about:blank")
            except Exception:
                logging.warning(
                    "Shared page failed to reset to about:blank; replacing it with a new page"
                )
                session_page.close()
                session_page = None
    if session_page is None:
        _session_page_holder.clear()
        session_page = _new_session_page(browser)
        _session_page_holder.append(session_page)
        session_page.goto("about:blank")
    # Reset screen size to 1080p
    session_page.set_viewport_size({"width": 1920, "height": 1080})
    return session_page


@pytest.fixture(scope="session")
def connect_options() -> dict[str, str] | None:
    ws_endpoint = os.getenv("PW_TEST_CONNECT_WS_ENDPOINT")
    if not ws_endpoint:
        return None

    endpoint_arg = (
        "endpoint"
        if "endpoint" in signature(BrowserType.connect).parameters
        else "ws_endpoint"
    )
    options = {endpoint_arg: ws_endpoint}
    expose_network = os.getenv("PW_TEST_CONNECT_EXPOSE_NETWORK")
    if expose_network:
        options["expose_network"] = expose_network

    return options


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
