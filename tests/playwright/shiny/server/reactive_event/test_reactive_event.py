from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    btn_count = controller.InputActionButton(page, "btn_count")
    btn_trigger = controller.InputActionButton(page, "btn_trigger")
    txt_immediate = controller.OutputTextVerbatim(page, "txt_immediate")
    txt_render_delayed = controller.OutputTextVerbatim(page, "txt_render_delayed")
    txt_reactive_delayed = controller.OutputTextVerbatim(page, "txt_reactive_delayed")

    txt_immediate.expect_value("0")
    txt_render_delayed.expect_value("")
    txt_reactive_delayed.expect_value("")

    btn_count.click()
    btn_count.click()
    btn_count.click()
    txt_immediate.expect_value("3")
    txt_render_delayed.expect_value("")
    txt_reactive_delayed.expect_value("")

    btn_trigger.click()
    txt_immediate.expect_value("3")
    txt_render_delayed.expect_value("3")
    txt_reactive_delayed.expect_value("3")

    btn_count.click()
    btn_count.click()
    txt_immediate.expect_value("5")
    txt_render_delayed.expect_value("3")
    txt_reactive_delayed.expect_value("3")

    btn_trigger.click()
    txt_immediate.expect_value("5")
    txt_render_delayed.expect_value("5")
    txt_reactive_delayed.expect_value("5")
