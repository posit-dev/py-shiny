from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_tooltip_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Get tooltip controller
    tooltip = controller.Tooltip(page, "tooltip_id")

    # Get button controllers
    show_btn = controller.InputActionButton(page, "btn_show")
    close_btn = controller.InputActionButton(page, "btn_close")
    update_btn = controller.InputActionButton(page, "btn_update")
    tooltip_btn = controller.InputActionButton(page, "btn_w_tooltip")

    # Test initial button labels
    show_btn.expect_label("Show tooltip")
    close_btn.expect_label("Close tooltip")
    update_btn.expect_label("Update tooltip")
    tooltip_btn.expect_label("Hover over me!")

    # Test initial tooltip state and content
    tooltip.expect_active(False)
    show_btn.click()
    tooltip.expect_body("Initial tooltip message - try the buttons above!")
    tooltip.expect_placement("right")

    # Test showing tooltip
    tooltip.expect_active(True)

    # Test closing tooltip
    close_btn.click()
    tooltip.expect_active(False)

    # Test updating tooltip content
    update_btn.click()
    tooltip.expect_active(True)
    tooltip.expect_body("Tooltip updated 1 time!")

    close_btn.click()
    tooltip.expect_active(False)

    # Click update button again and verify content changes
    update_btn.click()
    tooltip.expect_active(True)
    tooltip.expect_body("Tooltip updated 2 times!")
