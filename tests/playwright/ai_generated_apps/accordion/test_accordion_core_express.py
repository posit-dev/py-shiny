from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])

# For this file, separate the tests to "prove" that the fixture exists for the whole module


def test_accordion_demo1(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test accordion
    accordion = controller.Accordion(page, "acc_demo")

    # Test initial state - Panel B and D should be open by default
    accordion.expect_multiple(True)

    # Test individual panels
    panel_a = accordion.accordion_panel("Panel A")
    panel_b = accordion.accordion_panel("Panel B")
    panel_c = accordion.accordion_panel("Panel C")
    panel_d = accordion.accordion_panel("Panel D")

    # Test initial states (open/closed)
    panel_a.expect_open(False)
    panel_b.expect_open(True)  # Should be open by default
    panel_c.expect_open(False)
    panel_d.expect_open(True)  # Should be open by default

    # Test panel labels
    panel_a.expect_label("Panel A")
    panel_b.expect_label("Panel B")
    panel_c.expect_label("Panel C")
    panel_d.expect_label("Panel D")


def test_accordion_demo2(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test accordion
    accordion = controller.Accordion(page, "acc_demo")

    # Test initial state - Panel B and D should be open by default
    accordion.expect_multiple(True)

    # Test individual panels
    panel_a = accordion.accordion_panel("Panel A")
    panel_b = accordion.accordion_panel("Panel B")
    panel_c = accordion.accordion_panel("Panel C")
    # panel_d = accordion.accordion_panel("Panel D")

    # Test panel content
    panel_a.expect_body("This is a basic accordion panel with default settings.")
    panel_b.expect_body("This panel has a custom star icon and is open by default.")
    panel_c.expect_body("This is another basic panel that starts closed.")

    # Test opening and closing panels
    panel_c.set(True)  # Open panel C
    panel_c.expect_open(True)

    panel_b.set(False)  # Close panel B
    panel_b.expect_open(False)

    # Test the output text showing currently open panels
    output_text = controller.OutputText(page, "selected_panels")
    output_text.expect_value("Currently open panels: ('Panel C', 'Panel D')")
