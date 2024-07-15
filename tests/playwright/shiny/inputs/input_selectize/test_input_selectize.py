from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_selectize_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    state1 = controller.InputSelectize(page, "state1")
    state2 = controller.InputSelectize(page, "state2")
    state3 = controller.InputSelectize(page, "state3")
    state4 = controller.InputSelectize(page, "state4")

    value1 = controller.OutputCode(page, "value1")
    value2 = controller.OutputCode(page, "value2")
    value3 = controller.OutputCode(page, "value3")
    value4 = controller.OutputCode(page, "value4")

    # -------------------------

    expect(state1.loc_label).to_have_text("Choose a state:")
    state1.expect_label("Choose a state:")

    state1.expect_choices(["NY", "NJ", "CT", "WA", "OR", "CA", "MN", "WI", "IA"])
    state1.expect_choice_labels(
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
    state1.expect_choice_groups(["East Coast", "West Coast", "Midwest"])

    state1.expect_multiple(True)

    state1.set(["IA", "CA"])

    state1.expect_selected(["IA", "CA"])

    value1.expect_value("('IA', 'CA')")

    # -------------------------

    state2.expect_label("Selectize Options")

    state2.expect_choices(["NY", "NJ", "CT", "WA", "OR", "CA", "MN", "WI", "IA"])
    state2.expect_choice_labels(
        [
            "Select New York",
            "Select New Jersey",
            "Select Connecticut",
            "Select Washington",
            "Select Oregon",
            "Select California",
            "Select Minnesota",
            "Select Wisconsin",
            "Select Iowa",
        ]
    )
    state2.expect_choice_groups(["East Coast", "West Coast", "Midwest"])

    state2.expect_multiple(True)

    state2.set(["IA", "CA"])

    state2.expect_selected(["IA", "CA"])
    value2.expect_value("('IA', 'CA')")

    # -------------------------

    state3.expect_label("Single Selectize")

    state3.expect_choices(["NY", "NJ", "CT"])

    state3.expect_choice_labels(
        [
            "New York",
            "New Jersey",
            "Connecticut",
        ]
    )

    state3.expect_multiple(False)

    state3.set(["NJ"])

    state3.expect_selected(["NJ"])
    value3.expect_value("NJ")

    # -------------------------

    state4.expect_label("Simple Selectize")

    state4.expect_choices(["New York", "New Jersey", "Connecticut"])

    state4.expect_choice_labels(
        [
            "New York",
            "New Jersey",
            "Connecticut",
        ]
    )

    state4.expect_multiple(False)

    state4.set(["New York"])

    state4.expect_selected(["New York"])
    value4.expect_value("New York")
