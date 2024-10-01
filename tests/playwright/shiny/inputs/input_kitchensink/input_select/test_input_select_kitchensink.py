from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_select_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    basic_select = controller.InputSelect(page, "basic_select")
    basic_select_txt = controller.OutputCode(page, "basic_result_txt")
    basic_select.expect_label("Default select")
    basic_select.expect_choices(["Apple", "Banana", "Cherry", "Date", "Elderberry"])
    basic_select.expect_choice_labels(
        ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
    )
    basic_select.expect_choice_groups([])
    basic_select_txt.expect_value("Apple")
    basic_select.expect_multiple(False)

    multiple_select = controller.InputSelect(page, "multi_select")
    multiple_select_txt = controller.OutputCode(page, "multi_result_txt")
    multiple_options = ["Banana", "Cherry"]
    multiple_select.set(multiple_options)
    multiple_select.expect_multiple(True)
    multiple_select_txt.expect_value("Banana, Cherry")

    select_with_selected = controller.InputSelect(page, "select_with_selected")
    select_with_selected_txt = controller.OutputCode(page, "select_with_selected_txt")
    select_with_selected.expect_selected("Cherry")
    select_with_selected_txt.expect_value("Cherry")

    select_with_width = controller.InputSelect(page, "width_select")
    select_with_width.expect_width("400px")

    select_with_labels = controller.InputSelect(page, "select_with_labels")
    select_with_labels.expect_choices(
        ["apple", "banana", "cherry", "date", "elderberry"]
    )
    select_with_labels.expect_choice_labels(
        ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
    )
    controller.OutputCode(page, "select_with_labels_txt").expect_value("apple")

    select_with_custom_size_and_dict = controller.InputSelect(
        page, "select_with_custom_size_and_dict"
    )

    select_with_custom_size_and_dict.expect_choice_groups(["Citrus", "Berries"])
    select_with_custom_size_and_dict.expect_choice_labels(
        [
            "Sweet and tangy",
            "Zesty and refreshing",
            "Bright and tart",
            "Juicy and sweet",
            "Tiny and antioxidant-rich",
            "Delicate and slightly tart",
        ]
    )

    # TODO-karan; Debug why this does not complete
    # page.set_default_timeout(100)
    # select_with_custom_size_and_dict.expect_choices(
    #     [
    #         "Orange",
    #         "Lemon",
    #         "Lime",
    #         "Strawberry",
    #         "Blueberry",
    #         "Raspberry",
    #     ],
    # )
    # select_with_custom_size_and_dict.expect_size("4")

    # # # TODO-karan; Should we implement this? Seems like the only way to determine which choices belong to which groups. While we're at it, we might as well test the labels.
    # # select_with_custom_size_and_dict.expect_choices({
    # #     "Citrus": {
    # #         "Orange": "Sweet and tangy",
    # #         "Lemon": "Zesty and refreshing",
    # #         "Lime": "Bright and tart",
    # #     },
    # #     "Berries": {
    # #         "Strawberry": "Juicy and sweet",
    # #         "Blueberry": "Tiny and antioxidant-rich",
    # #         "Raspberry": "Delicate and slightly tart",
    # #     },
    # # })
    # # This would also allow us to test the labels and values at the same time!
    # # select_with_custom_size_and_dict.expect_choices({
    # #     "Orange": "Sweet and tangy",
    # #     "Lemon": "Zesty and refreshing",
    # #     "Lime": "Bright and tart",
    # #     "Strawberry": "Juicy and sweet",
    # #     "Blueberry": "Tiny and antioxidant-rich",
    # #     "Raspberry": "Delicate and slightly tart",
    # # })
    # ------------------------------------
    # # If we get choices with no labels, should it be auto upgraded to a dictionary of `{FOO: FOO}`?
    # # ANSWER: No, unless we drop `expect_labels()` and `expect_choice_groups()` and just have `expect_choices()` handle everything.
    # # select_with_custom_size_and_dict.expect_choices([
    # #     "Orange",
    # #     "Lemon",
    # #     "Lime",
    # #     "Strawberry",
    # #     "Blueberry",
    # #     "Raspberry",
    # # ])
    # # Auto upgraded to: (which also asserts that there are no groups)
    # # select_with_custom_size_and_dict.expect_choices({
    # #     "Orange": "Orange",
    # #     "Lemon": "Lemon",
    # #     "Lime": "Lime",
    # #     "Strawberry": "Strawberry",
    # #     "Blueberry": "Blueberry",
    # #     "Raspberry": "Raspberry",
    # # })

    # # This should be auto upgraded from
    # # select_with_custom_size_and_dict.expect_choices({
    # #     "Citrus": [
    # #         "Orange",
    # #         "Lemon",
    # #         "Lime",
    # #     ],
    # #     "Berries": [
    # #         "Strawberry",
    # #         "Blueberry",
    # #         "Raspberry",
    # #     ],
    # # })
    # # to:
    # # select_with_custom_size_and_dict.expect_choices({
    # #     "Citrus": {
    # #         "Orange": "Orange",
    # #         "Lemon": "Lemon",
    # #         "Lime": "Lime",
    # #     },
    # #     "Berries": {
    # #         "Strawberry": "Strawberry",
    # #         "Blueberry": "Blueberry",
    # #         "Raspberry": "Raspberry",
    # #     },
    # # })
