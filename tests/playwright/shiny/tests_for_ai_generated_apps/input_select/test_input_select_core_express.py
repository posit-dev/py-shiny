from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_input_select_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic select with simple choices
    select1 = controller.InputSelect(page, "select1")
    select1.expect_label("Basic select (simple list)")
    select1.expect_choices(["A", "B", "C", "D"])
    select1.expect_selected("A")  # Test initial selection
    select1.expect_multiple(False)
    select1_value = controller.OutputText(page, "selected_value1")
    select1_value.expect_value("Selected: A")

    # Test select with dictionary choices
    select2 = controller.InputSelect(page, "select2")
    select2.expect_label("Select with dictionary choices")
    select2.expect_choices(["a", "b", "c"])
    select2.expect_choice_labels(["Option A", "Option B", "Option C"])
    select2.expect_selected("a")  # Test initial selection
    select2.expect_multiple(False)
    select2_value = controller.OutputText(page, "selected_value2")
    select2_value.expect_value("Selected: a")

    # Test select with grouped choices
    select3 = controller.InputSelect(page, "select3")
    select3.expect_label("Select with grouped choices")
    select3.expect_choices(["g1a", "g1b", "g2a", "g2b"])
    select3.expect_choice_labels(
        ["Group 1 - A", "Group 1 - B", "Group 2 - A", "Group 2 - B"]
    )
    select3.expect_choice_groups(["Group 1", "Group 2"])
    select3.expect_selected("g1a")  # Test initial selection
    select3.expect_multiple(False)
    select3_value = controller.OutputText(page, "selected_value3")
    select3_value.expect_value("Selected: g1a")

    # Test multiple select
    select4 = controller.InputSelect(page, "select4")
    select4.expect_label("Multiple select")
    select4.expect_choices(["A", "B", "C", "D"])
    select4.expect_selected(["A", "B"])  # Test initial multiple selection
    select4.expect_multiple(True)
    select4_value = controller.OutputText(page, "selected_value4")
    select4_value.expect_value("Selected: ('A', 'B')")

    # Test select with custom width
    select5 = controller.InputSelect(page, "select5")
    select5.expect_label("Select with custom width")
    select5.expect_choices(["A", "B", "C", "D"])
    select5.expect_width("200px")
    select5.expect_multiple(False)
    select5_value = controller.OutputText(page, "selected_value5")
    select5_value.expect_value("Selected: A")

    # Test select with size parameter
    select6 = controller.InputSelect(page, "select6")
    select6.expect_label("Select with size parameter")
    select6.expect_choices(["A", "B", "C", "D"])
    select6.expect_size("4")
    select6.expect_multiple(False)
    select6_value = controller.OutputText(page, "selected_value6")
    select6_value.expect_value("Selected: A")
