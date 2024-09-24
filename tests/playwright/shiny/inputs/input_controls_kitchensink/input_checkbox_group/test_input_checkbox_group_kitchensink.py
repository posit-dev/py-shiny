from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_checkbox_group_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputCheckboxGroup(page, "default")
    default.expect_label("Basic Checkbox Group")
    default.expect_selected([])

    selected = controller.InputCheckboxGroup(page, "selected")
    selected.expect_selected(["Option B", "Option C"])

    width = controller.InputCheckboxGroup(page, "width")
    width.expect_width("30px")

    inline = controller.InputCheckboxGroup(page, "inline")
    inline.expect_inline(True)
    inline.set(["Option A", "Option D"])
    inline.expect_selected(["Option A", "Option D"])

    inline_code = controller.OutputCode(page, "inline_val_txt")
    inline_code.expect_value("You chose Option A, Option D")

    dict_values = controller.InputCheckboxGroup(page, "dict_values")
    dict_values.expect_selected([])
    dict_values.set(["value1", "value4"])
    dict_values.expect_selected(["value1", "value4"])

    dict_values_code = controller.OutputCode(page, "dict_value_txt")
    dict_values_code.expect_value("You chose value1, value4")
