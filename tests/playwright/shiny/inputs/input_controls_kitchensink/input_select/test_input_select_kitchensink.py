from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_select_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    basic_select = controller.InputSelect(page, "basic_select")
    basic_select_txt = controller.OutputText(page, "basic_result_txt")
    basic_select.expect_label("Default select")
    basic_select_txt.expect_value("Basic select: Apple")
    basic_select.expect_multiple(False)

    multiple_select = controller.InputSelect(page, "multi_select")
    multiple_select_txt = controller.OutputText(page, "multi_result_txt")
    multiple_options = ["Banana", "Cherry"]
    multiple_select.set(multiple_options)
    multiple_select.expect_multiple(True)
    multiple_select_txt.expect_value("Multi select: Banana, Cherry")

    select_with_selected = controller.InputSelect(page, "select_with_selected")
    select_with_selected_txt = controller.OutputText(page, "select_with_selected_txt")
    select_with_selected.expect_selected("Cherry")
    select_with_selected_txt.expect_value("Select with selected: Cherry")

    select_with_width = controller.InputSelect(page, "width_select")
    select_with_width.expect_width("400px")

    select_with_custom_size_and_dict = controller.InputSelect(
        page, "select_with_custom_size_and_dict"
    )
    select_with_custom_size_and_dict.expect_choice_groups(["Citrus", "Berries"])
    select_with_custom_size_and_dict.expect_size("4")
