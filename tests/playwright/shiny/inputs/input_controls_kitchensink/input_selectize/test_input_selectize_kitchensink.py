from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_selectize_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    basic_selectize = controller.InputSelectize(page, "basic_selectize")
    basic_select_txt = controller.OutputText(page, "basic_result_txt")
    basic_selectize.expect_label("Default selectize")
    basic_select_txt.expect_value("Basic select: Apple")

    multiple_selectize = controller.InputSelectize(page, "multi_selectize")
    multiple_selectize_txt = controller.OutputText(page, "multi_result_txt")
    multiple_selectize.set(["Banana", "Cherry"])
    multiple_selectize_txt.expect_value("Multi select: Banana, Cherry")

    selectize_with_selected = controller.InputSelectize(page, "selectize_with_selected")
    selectize_with_selected_txt = controller.OutputText(page, "selected_result_txt")
    selectize_with_selected.expect_selected(["Cherry"])
    selectize_with_selected_txt.expect_value("Select with selected: Cherry")

    selectize_width_close_button = controller.InputSelectize(
        page, "selectize_width_close_button"
    )
    selectize_width_close_button_txt = controller.OutputText(
        page, "selectize_width_close_button_txt"
    )
    selectize_width_close_button_txt.expect_value("Selectize with close button: Orange")
    selectize_width_close_button.expect_width("400px")
    selectize_width_close_button.clear_selection()
    selectize_width_close_button_txt.expect_value(
        "Selectize with close button: "
    )  # Expecting empty after clear
