from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_accordion_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test accordion with ID "acc"
    accordion = controller.Accordion(page, "acc")

    # Test that multiple panels can be open
    accordion.expect_multiple(True)

    # Test that accordion is initially open
    panel1 = accordion.accordion_panel("Basic Panel")
    panel2 = accordion.accordion_panel("panel2")
    panel3 = accordion.accordion_panel("panel3")
    panel4 = accordion.accordion_panel("panel4")

    # Test initial state
    panel1.expect_open(True)
    panel2.expect_open(True)
    panel3.expect_open(True)
    panel4.expect_open(True)

    # Test panel labels
    panel1.expect_label("Basic Panel")
    panel2.expect_label("Panel with Value")
    panel3.expect_label("Panel with Icon")
    panel4.expect_label("Panel with Custom Attributes")

    # Test panel content
    panel1.expect_body("This is a basic panel with just a title parameter")
    panel2.expect_body("This panel has both a title and a value parameter")
    panel3.expect_body("This panel includes an icon parameter using Font Awesome")
    panel4.expect_body("This panel demonstrates custom attributes (class and style)")

    # Test icons (presence/absence)
    panel1.expect_icon(False)  # First panel has no icon
    panel2.expect_icon(False)  # Second panel has no icon
    panel3.expect_icon(True)  # Third panel has an icon
    panel4.expect_icon(True)  # Fourth panel has an icon

    # Test closing and opening panels
    panel1.set(False)
    panel1.expect_open(False)
    panel1.set(True)
    panel1.expect_open(True)

    # Test output text that shows selected panel
    selected_text = controller.OutputText(page, "selected_panel")
    selected_text.expect_value(
        "Currently selected panel: ('Basic Panel', 'panel2', 'panel3', 'panel4')"
    )
