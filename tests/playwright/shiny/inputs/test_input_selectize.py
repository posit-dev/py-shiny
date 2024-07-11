from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_selectize")


def test_input_selectize_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    state = controller.InputSelectize(page, "state")

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

    state.expect_multiple(True)

    state.set(["Iowa", "California"])

    state.expect_selected(["IA", "CA"])
