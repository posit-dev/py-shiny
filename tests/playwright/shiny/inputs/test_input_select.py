from conftest import create_doc_example_core_fixture

from shiny.test import Page, ShinyAppProc, expect
from shiny.test._controls import InputSelect

app = create_doc_example_core_fixture("input_select")


def test_input_select_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    state = InputSelect(page, "state")

    expect(state.loc_label).to_have_text("Choose a state:")
    state.expect_label("Choose a state:")

    state.expect_choices(["NY", "NJ", "CT", "WA", "OR", "CA", "MN", "WI", "IA"])
    state.expect_choice_labels(
        [
            "New York",
            "New Jersey",
            "Connecticut",
            "Washington",
            "Oregon",
            "California",
            "Minnesota",
            "Wisconsin",
            "Iowa",
        ]
    )
    state.expect_choice_groups(["East Coast", "West Coast", "Midwest"])

    state.expect_selected("NY")
    state.expect_multiple(False)
    state.expect_selectize(False)

    state.expect_width(None)

    state.set("IA")

    state.expect_selected("IA")
