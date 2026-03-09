# pyright: reportUnknownMemberType=false
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_stable_during_slow_effect(page: Page, local_app: ShinyAppProc) -> None:
    """
    Click button twice rapidly while a slow effect is executing.
    The log should show [1, 2] -- each click processed with its stable value.
    """
    page.goto(local_app.url)

    btn = controller.InputActionButton(page, "btn")
    log_output = controller.OutputTextVerbatim(page, "effect_log")

    btn.click()
    btn.click()

    log_output.expect_value("[1, 2]", timeout=5000)


def test_all_rapid_clicks_processed(page: Page, local_app: ShinyAppProc) -> None:
    """
    Click 3 times rapidly. All 3 should be processed via the cycle queue.
    """
    page.goto(local_app.url)

    btn = controller.InputActionButton(page, "btn")
    log_output = controller.OutputTextVerbatim(page, "effect_log")

    btn.click()
    btn.click()
    btn.click()

    log_output.expect_value("[1, 2, 3]", timeout=8000)
