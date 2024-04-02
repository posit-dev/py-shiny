from conftest import ShinyAppProc
from controls import InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    btn_count = InputActionButton(page, "btn_count")
    btn_trigger = InputActionButton(page, "btn_trigger")
    txt_immediate = OutputTextVerbatim(page, "txt_immediate")
    txt_render_delayed = OutputTextVerbatim(page, "txt_render_delayed")
    txt_reactive_delayed = OutputTextVerbatim(page, "txt_reactive_delayed")

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
