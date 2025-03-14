from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_checkbox_group_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Get the checkbox group controller
    colors = controller.InputCheckboxGroup(page, "colors")
    selected_output = controller.OutputText(page, "selected_colors")

    # Test initial state
    colors.expect_label("Choose colors")
    colors.expect_choices(["red", "green", "blue"])
    colors.expect_selected(["red", "blue"])  # Check pre-selected values
    colors.expect_inline(True)
    colors.expect_width("300px")
    selected_output.expect_value("You selected: red, blue")

    # Test selecting different combinations
    colors.set(["green"])
    selected_output.expect_value("You selected: green")

    # Test selecting multiple values
    colors.set(["red", "green", "blue"])
    selected_output.expect_value("You selected: red, green, blue")

    # Test deselecting all values
    colors.set([])
    selected_output.expect_value("No colors selected")
