from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_checkbox_group_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputRadioButtons(page, "default")
    default.expect_label("Default radio buttons")
    default.expect_selected("Option A")
    controller.OutputCode(page, "default_txt").expect_value("Option A")

    selected = controller.InputRadioButtons(page, "selected")
    selected.expect_selected("Option B")
    controller.OutputCode(page, "selected_txt").expect_value("Option B")

    width = controller.InputRadioButtons(page, "width")
    width.expect_width("30px")
    width.expect_inline(False)

    inline = controller.InputRadioButtons(page, "inline")
    inline.expect_inline(True)

    choices_dict = controller.InputRadioButtons(page, "choices_dict")
    choices_dict.expect_selected("a")
    controller.OutputCode(page, "choices_dict_txt").expect_value("a")
    choices_dict.set("c")
    choices_dict.expect_selected("c")
    controller.OutputCode(page, "choices_dict_txt").expect_value("c")
