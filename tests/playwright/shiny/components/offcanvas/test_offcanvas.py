from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_offcanvas_trigger(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    panel = controller.Offcanvas(page, "trigger_panel")
    state = controller.OutputTextVerbatim(page, "trigger_state")

    panel.expect_open(False)
    state.expect_value("closed")

    controller.InputActionButton(page, "open_btn").click()
    panel.expect_open(True)
    panel.expect_body("Panel via trigger.")
    state.expect_value("open")

    panel.close()
    panel.expect_open(False)
    state.expect_value("closed")


def test_offcanvas_server_toggle(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    panel = controller.Offcanvas(page, "server_panel")
    state = controller.OutputTextVerbatim(page, "server_state")

    panel.expect_open(False)
    state.expect_value("closed")

    controller.InputActionButton(page, "show_btn").click()
    panel.expect_open(True)
    state.expect_value("open")

    controller.InputActionButton(page, "hide_btn").click()
    panel.expect_open(False)
    state.expect_value("closed")
