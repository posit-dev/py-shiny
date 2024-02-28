from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputSelectize
from playwright.sync_api import Page, expect

app = create_doc_example_core_fixture("input_selectize")


def test_input_selectize_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    state = InputSelectize(page, "state")

    expect(state.loc_label).to_have_text("Choose a state:")
    state.expect_label("Choose a state:")

    # TODO: This test was being run against input_select, not input_selectize
    # and none of these expectations pass. We need to add additional test methods
    # for the InputSelectize class to test this behaviour.
    # https://github.com/posit-dev/py-shiny/issues/1100

    # state.expect_choices(["NY", "NJ", "CT", "WA", "OR", "CA", "MN", "WI", "IA"])
    # state.expect_choice_labels(
    #     [
    #         "New York",
    #         "New Jersey",
    #         "Connecticut",
    #         "Washington",
    #         "Oregon",
    #         "California",
    #         "Minnesota",
    #         "Wisconsin",
    #         "Iowa",
    #     ]
    # state.expect_choice_groups(["East Coast", "West Coast", "Midwest"])

    # state.expect_multiple(True)

    # state.expect_width(None)

    # state.set("Iowa")

    # state.expect_selected("IA")
