import re

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_offcanvas_trigger(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    panel = controller.Offcanvas(page, "trigger_panel")
    state = controller.OutputCode(page, "trigger_state")

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
    state = controller.OutputCode(page, "server_state")

    panel.expect_open(False)
    state.expect_value("closed")

    controller.InputActionButton(page, "show_btn").click()
    panel.expect_open(True)
    state.expect_value("open")

    controller.InputActionButton(page, "hide_btn").click()
    panel.expect_open(False)
    state.expect_value("closed")


def test_show_offcanvas_by_id(page: Page, local_app: ShinyAppProc) -> None:
    """show_offcanvas() with a bare string reveals an existing panel by id."""
    page.goto(local_app.url)

    panel = controller.Offcanvas(page, "existing_panel")
    panel.expect_open(False)

    controller.InputActionButton(page, "show_existing_btn").click()
    panel.expect_open(True)
    panel.expect_body("Panel declared for id-based reveal.")


def test_show_offcanvas_wraps_content(page: Page, local_app: ShinyAppProc) -> None:
    """show_offcanvas() with bare tag content wraps it in a new anonymous panel."""
    page.goto(local_app.url)

    controller.InputActionButton(page, "show_content_btn").click()

    new_panel = page.locator("bslib-offcanvas.show")
    expect(new_panel).to_be_visible()
    expect(new_panel.locator(".offcanvas-body")).to_have_text("Wrapped content panel.")


def test_show_offcanvas_bad_id_raises(page: Page, local_app: ShinyAppProc) -> None:
    """show_offcanvas() raises a ValueError for a string that looks like body text."""
    page.goto(local_app.url)

    controller.InputActionButton(page, "show_bad_id_btn").click()

    error_output = controller.OutputText(page, "bad_id_error")
    error_output.expect_value(re.compile("looks like body text"))
