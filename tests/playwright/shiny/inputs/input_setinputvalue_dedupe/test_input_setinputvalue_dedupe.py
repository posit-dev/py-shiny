import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.only_browser("chromium")
def test_setinputvalue_dedupe(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    int_default_count = controller.OutputTextVerbatim(page, "int_default_count")
    int_event_count = controller.OutputTextVerbatim(page, "int_event_count")
    list_default_count = controller.OutputTextVerbatim(page, "list_default_count")
    list_event_count = controller.OutputTextVerbatim(page, "list_event_count")

    int_default_count.expect_value("0")
    int_event_count.expect_value("0")
    list_default_count.expect_value("0")
    list_event_count.expect_value("0")

    btn_int_default = page.locator("#btn_int_default")
    btn_int_event = page.locator("#btn_int_event")
    btn_list_default = page.locator("#btn_list_default")
    btn_list_event = page.locator("#btn_list_event")

    # Click both default and event buttons in the same loop. The event-priority
    # assertion (expect_value(str(i))) acts as a synchronization point: by the
    # time the event counter has incremented on the server, the default-priority
    # click from the same iteration has also been processed. If the default
    # counter were to increment beyond 1, it would be caught here.
    for i in range(1, 4):
        btn_int_default.click()
        btn_int_event.click()
        int_event_count.expect_value(str(i))
        int_default_count.expect_value("1")

    for i in range(1, 4):
        btn_list_default.click()
        btn_list_event.click()
        list_event_count.expect_value(str(i))
        list_default_count.expect_value("1")


@pytest.mark.only_browser("chromium")
def test_setinputvalue_event_priority_strings(
    page: Page, local_app: ShinyAppProc
) -> None:
    """Regression test for https://github.com/posit-dev/py-shiny/issues/1600"""
    page.goto(local_app.url)

    result = controller.OutputTextVerbatim(page, "str_event_count")
    result.expect_value("0")

    btn_empty = page.locator("#btn_str_empty")
    btn_nonempty = page.locator("#btn_str_nonempty")

    # Empty string "" is interned by CPython, so repeated event-priority
    # sends of "" must still fire the reactive effect each time.
    for i in range(1, 4):
        btn_empty.click()
        result.expect_value(str(i))

    # Non-empty string "x=1" may or may not be interned depending on
    # context; either way it should fire every time.
    for i in range(4, 7):
        btn_nonempty.click()
        result.expect_value(str(i))
