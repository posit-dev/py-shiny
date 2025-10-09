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


def test_set_filter_accepts_single_dict(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    penguin_df = controller.OutputDataFrame(page, "penguins_df")
    penguin_code = controller.OutputCode(page, "penguins_code")

    penguin_df.set_filter({"col": 0, "value": "Chinstrap"})

    penguin_code.expect_value("({'col': 0, 'value': 'Chinstrap'},)")
    expect(penguin_df.loc_column_filter.nth(0).locator("input")).to_have_value(
        "Chinstrap"
    )


def test_set_filter_accepts_list(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    penguin_df = controller.OutputDataFrame(page, "penguins_df")
    penguin_code = controller.OutputCode(page, "penguins_code")

    penguin_df.set_filter(
        [
            {"col": 0, "value": "Gentoo"},
            {"col": 2, "value": (45, 50)},
        ]
    )

    penguin_code.expect_value(
        "({'col': 0, 'value': 'Gentoo'}, {'col': 2, 'value': (45, 50)})"
    )

    species_filter = penguin_df.loc_column_filter.nth(0).locator("input")
    length_filter = penguin_df.loc_column_filter.nth(2).locator("div > input")

    expect(species_filter).to_have_value("Gentoo")
    expect(length_filter.nth(0)).to_have_value("45")
    expect(length_filter.nth(1)).to_have_value("50")


def test_set_filter_accepts_tuple(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    penguin_df = controller.OutputDataFrame(page, "penguins_df")
    penguin_code = controller.OutputCode(page, "penguins_code")

    penguin_df.set_filter(
        (
            {"col": 3, "value": (None, 17)},
            {"col": 0, "value": "Adelie"},
        )  # type: ignore[arg-type]
    )

    penguin_code.expect_value(
        "({'col': 0, 'value': 'Adelie'}, {'col': 3, 'value': (None, 17)})"
    )

    species_filter = penguin_df.loc_column_filter.nth(0).locator("input")
    depth_filter = penguin_df.loc_column_filter.nth(3).locator("div > input")

    expect(species_filter).to_have_value("Adelie")
    expect(depth_filter.nth(0)).to_have_value("")
    expect(depth_filter.nth(1)).to_have_value("17")


def test_set_filter_accepts_multi_column_mapping(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    penguin_df = controller.OutputDataFrame(page, "penguins_df")
    penguin_code = controller.OutputCode(page, "penguins_code")

    penguin_df.set_filter(
        {
            "col": [0, 1],
            "value": ["Gentoo", "Biscoe"],
        }  # type: ignore[arg-type]
    )

    penguin_code.expect_value(
        "({'col': 0, 'value': 'Gentoo'}, {'col': 1, 'value': 'Biscoe'})"
    )

    species_filter = penguin_df.loc_column_filter.nth(0).locator("input")
    island_filter = penguin_df.loc_column_filter.nth(1).locator("input")

    expect(species_filter).to_have_value("Gentoo")
    expect(island_filter).to_have_value("Biscoe")


def test_set_filter_none_clears_inputs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    penguin_df = controller.OutputDataFrame(page, "penguins_df")
    penguin_code = controller.OutputCode(page, "penguins_code")

    penguin_df.set_filter(
        [
            {"col": 0, "value": "Gentoo"},
            {"col": 2, "value": (45, 50)},
        ]
    )

    penguin_code.expect_value(
        "({'col': 0, 'value': 'Gentoo'}, {'col': 2, 'value': (45, 50)})"
    )
    penguin_df.set_filter(None)

    penguin_code.expect_value("()")

    filter_inputs = penguin_df.loc_column_filter.locator("input")
    for i in range(filter_inputs.count()):
        expect(filter_inputs.nth(i)).to_have_value("")
