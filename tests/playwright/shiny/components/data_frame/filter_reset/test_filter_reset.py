from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_filters_are_reset(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    penguin_df = controller.OutputDataFrame(page, "penguins_df")
    penguin_code = controller.OutputCode(page, "penguins_code")
    update_filters = controller.InputActionButton(page, "update_filters")
    reset_filters = controller.InputActionButton(page, "reset_filters")

    filter_inputs = penguin_df.loc_column_filter.locator("input")

    expect(filter_inputs).to_have_count(8 + 5)  # 8 columns including 5 numeric columns

    penguin_code.expect_value("()")
    for i in range(filter_inputs.count()):
        expect(filter_inputs.nth(i)).to_have_value("")

    update_filters.click()

    penguin_code.expect_value(
        "("
        "{'col': 0, 'value': 'Gentoo'}, "
        "{'col': 2, 'value': (50, None)}, "
        "{'col': 3, 'value': (None, 17)}, "
        "{'col': 4, 'value': (220, 225)}"
        ")"
    )
    for i, value in enumerate(
        ["Gentoo", "", "50", "", "", "17", "220", "225", "", "", "", "", ""]
    ):
        expect(filter_inputs.nth(i)).to_have_value(value)

    reset_filters.click()

    penguin_code.expect_value("()")
    for i in range(filter_inputs.count()):
        expect(filter_inputs.nth(i)).to_have_value("")
