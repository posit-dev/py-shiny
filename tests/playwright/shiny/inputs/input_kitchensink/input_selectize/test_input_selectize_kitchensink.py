from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_selectize_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    basic_selectize = controller.InputSelectize(page, "basic_selectize")
    basic_select_txt = controller.OutputText(page, "basic_result_txt")
    # # TODO-karan; Debug why this does not complete
    # basic_selectize.expect_choices(["Apple", "Banana", "Cherry", "Date", "Elderberry"])
    basic_selectize.expect_choice_labels(
        [
            "Apple",
            "Banana",
            "Cherry",
            "Date",
            "Elderberry",
        ]
    )
    basic_selectize.expect_choice_groups([])
    basic_selectize.expect_label("Default selectize")
    basic_select_txt.expect_value("Apple")
    basic_selectize.expect_multiple(False)

    selectize_with_label = controller.InputSelectize(page, "selectize_with_label")
    selectize_with_label_txt = controller.OutputText(page, "selectize_with_label_txt")
    # # TODO-karan; Debug why this does not complete
    # selectize_with_label.expect_choices(
    #     ["apple", "banana", "cherry", "date", "elderberry"]
    # )
    selectize_with_label.expect_choice_labels(
        [
            "Apple",
            "Banana",
            "Cherry",
            "Date",
            "Elderberry",
        ]
    )
    selectize_with_label.expect_choice_groups([])
    selectize_with_label_txt.expect_value("apple")

    multiple_selectize = controller.InputSelectize(page, "multi_selectize")
    multiple_selectize_txt = controller.OutputText(page, "multi_result_txt")
    multiple_options = ["Banana", "Cherry"]
    multiple_selectize.set(multiple_options)
    multiple_selectize.expect_selected(["Banana", "Cherry"])
    multiple_selectize_txt.expect_value("Banana, Cherry")
    for option in multiple_options:
        # click on the remove button for each selected option
        multiple_selectize.loc.locator(
            f"+ div.plugin-remove_button > .has-options > .item[data-value={option}] > .remove"
        ).click()
        page.keyboard.press(
            "Escape"
        )  # to remove dropdown from blocking access to other selectize inputs
    multiple_selectize_txt.expect_value("")
    multiple_selectize.expect_multiple(True)

    selectize_with_selected = controller.InputSelectize(page, "selectize_with_selected")
    selectize_with_selected_txt = controller.OutputText(page, "selected_result_txt")
    selectize_with_selected.expect_selected(["Cherry"])
    selectize_with_selected_txt.expect_value("Cherry")

    selectize_width_close_button = controller.InputSelectize(
        page, "selectize_width_close_button"
    )
    selectize_width_close_button_txt = controller.OutputText(
        page, "selectize_width_close_button_txt"
    )
    selectize_width_close_button_txt.expect_value("Orange")
    selectize_width_close_button.expect_width("400px")
    selectize_width_close_button.expect_choice_groups(["Citrus", "Berries"])
    # # TODO-karan; Debug why this does not complete
    # selectize_width_close_button.expect_choices(
    #     ["Orange", "Lemon", "Lime", "Strawberry", "Blueberry", "Raspberry"]
    # )
    selectize_width_close_button.expect_choice_labels(
        [
            "Sweet and tangy",
            "Zesty and refreshing",
            "Bright and tart",
            "Juicy and sweet",
            "Tiny and antioxidant-rich",
            "Delicate and slightly tart",
        ]
    )
    selectize_width_close_button.loc.locator("..").locator(
        "> div.plugin-clear_button > a.clear"
    ).click()  # Clear default selection
    selectize_width_close_button_txt.expect_value("")  # Expecting empty after clear
