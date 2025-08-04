from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_accordion_and_buttons(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    accordion = controller.Accordion(page, "my_accordion")
    update_button = controller.InputActionButton(page, "update_button")
    add_panel_button = controller.InputActionButton(page, "add_panel_button")

    accordion.expect_panels(["About", "Panel 1", "panel_2_val"])

    about_panel = accordion.accordion_panel("About")
    about_panel.expect_label("About")
    about_panel.expect_body("This is a simple Shiny app.")

    panel_1 = accordion.accordion_panel("Panel 1")
    panel_1.expect_label("Panel 1")
    panel_1.expect_body("Some initial content for Panel 1.")

    panel_2 = accordion.accordion_panel("panel_2_val")
    panel_2.expect_label("Panel 2")
    panel_2.expect_body("Some initial content for Panel 2.")

    update_button.expect_label("Update Panel 2")
    update_button.click()

    panel_2.expect_label("Panel 2 (Updated)")

    add_panel_button.expect_label("Add New Panel")
    add_panel_button.click()

    accordion.expect_panels(["About", "Panel 1", "panel_2_val", "Panel 3"])

    panel_3 = accordion.accordion_panel("Panel 3")
    panel_3.expect_label("Panel 3")

    add_panel_button.click()

    accordion.expect_panels(["About", "Panel 1", "panel_2_val", "Panel 3", "Panel 4"])

    panel_4 = accordion.accordion_panel("Panel 4")
    panel_4.expect_label("Panel 4")
