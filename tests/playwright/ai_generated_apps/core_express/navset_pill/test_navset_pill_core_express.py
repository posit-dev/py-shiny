from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_navset_pill_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test navset pill
    navset = controller.NavsetPill(page, "pills")
    selected_panel_text = controller.OutputText(page, "selected_panel")

    # Test initial state
    navset.expect_nav_titles(["A", "B", "C"])
    navset.expect_nav_values(["A", "B", "C"])
    navset.expect_value("A")  # First panel should be selected by default
    selected_panel_text.expect_value("Currently selected panel: A")

    # Test Panel A components
    slider = controller.InputSlider(page, "n1")
    panel_a_text = controller.OutputText(page, "panel_a_text")

    slider.expect_label("N1")
    slider.expect_min("0")
    slider.expect_max("100")
    slider.expect_value("20")
    panel_a_text.expect_value("Value of n1: 20")

    # Change slider value and verify
    slider.set("50")
    panel_a_text.expect_value("Value of n1: 50")

    # Switch to Panel B and test its components
    navset.set("B")
    navset.expect_value("B")
    selected_panel_text.expect_value("Currently selected panel: B")

    numeric = controller.InputNumeric(page, "n2")
    panel_b_text = controller.OutputText(page, "panel_b_text")

    numeric.expect_label("N2")
    numeric.expect_value("10")
    panel_b_text.expect_value("Value of n2: 10")

    # Change numeric value and verify
    numeric.set("25")
    panel_b_text.expect_value("Value of n2: 25")

    # Switch to Panel C and test its components
    navset.set("C")
    navset.expect_value("C")
    selected_panel_text.expect_value("Currently selected panel: C")

    text_input = controller.InputText(page, "txt")
    panel_c_text = controller.OutputText(page, "panel_c_text")

    text_input.expect_label("Enter text")
    text_input.expect_value("Hello")
    panel_c_text.expect_value("You entered: Hello")

    # Change text value and verify
    text_input.set("Testing")
    panel_c_text.expect_value("You entered: Testing")
