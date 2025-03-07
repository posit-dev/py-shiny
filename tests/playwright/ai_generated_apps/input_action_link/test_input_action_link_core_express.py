from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_action_link_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test first card
    card1 = controller.Card(page, "card1")
    card1.expect_header("Action Link Demo")
    card1.expect_height("300px")
    card1.expect_full_screen_available(True)

    # Test second card
    card2 = controller.Card(page, "card2")
    card2.expect_header("Click History")
    card2.expect_height("300px")
    card2.expect_full_screen_available(True)

    # Test action link
    demo_link = controller.InputActionLink(page, "demo_link")
    demo_link.expect_label("Click Me!")

    # Test initial states of outputs
    output_text = controller.OutputText(page, "link_clicks")
    output_text.expect_value("The link has been clicked 0 times")

    history_text = controller.OutputText(page, "click_history")
    history_text.expect_value("No clicks yet!")

    # Test interaction - first click
    demo_link.click()
    output_text.expect_value("The link has been clicked 1 times")
    history_text.expect_value("First click recorded!")

    # Test interaction - second click
    demo_link.click()
    output_text.expect_value("The link has been clicked 2 times")
    history_text.expect_value("You've clicked 2 times. Keep going!")
