from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_action_buttons(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic button (btn1)
    btn1 = controller.InputActionButton(page, "btn1")
    btn1.expect_label("Basic Button")
    btn1.expect_width("200px")

    # Test button with icon (btn2)
    btn2 = controller.InputActionButton(page, "btn2")
    btn2.expect_label("Disabled Button with Icon")

    # Test styled button (btn3)
    btn3 = controller.InputActionButton(page, "btn3")
    btn3.expect_label("Styled Button")

    # Test initial click counts
    click_counts = controller.OutputText(page, "click_counts")
    click_counts.expect_value(
        "Button 1 clicks: 0\nButton 2 clicks: 0\nButton 3 clicks: 0"
    )

    # Test clicking btn1 and verify count updates
    btn1.click()
    click_counts.expect_value(
        "Button 1 clicks: 1\nButton 2 clicks: 0\nButton 3 clicks: 0"
    )

    # Test clicking btn3 and verify count updates
    btn3.click()
    click_counts.expect_value(
        "Button 1 clicks: 1\nButton 2 clicks: 0\nButton 3 clicks: 1"
    )

    # btn2 is disabled, so we don't test clicking it
