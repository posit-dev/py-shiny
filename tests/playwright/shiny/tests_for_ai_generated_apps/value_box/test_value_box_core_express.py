from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_value_boxes(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test left-center value box
    left_center_box = controller.ValueBox(page, "left_center_value_box")
    left_center_box.expect_title("Revenue")
    left_center_box.expect_value("$5.2M")

    # Test top-right value box
    top_right_box = controller.ValueBox(page, "top_right_value_box")
    top_right_box.expect_title("Active Users")
    top_right_box.expect_value("2.4K")
    top_right_box.expect_height("200px")

    # Test bottom value box
    bottom_box = controller.ValueBox(page, "bottom_value_box")
    bottom_box.expect_title("Conversion Rate")
    bottom_box.expect_value("3.8%")
    bottom_box.expect_height("200px")

    # Test full screen value box
    full_screen_box = controller.ValueBox(page, "full_screen_value_box")
    full_screen_box.expect_title("Total Sales")
    full_screen_box.expect_value("8,742")
    full_screen_box.expect_height("600px")
    full_screen_box.expect_full_screen_available(True)

    # Test custom background value box
    custom_bg_box = controller.ValueBox(page, "custom_bg_value_box")
    custom_bg_box.expect_title("Pending Orders")
    custom_bg_box.expect_value("156")
    custom_bg_box.expect_height("200px")
