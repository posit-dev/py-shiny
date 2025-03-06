from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_switch_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test card1
    card1 = controller.Card(page, "card1")
    card1.expect_header("Switch Demo")
    card1.expect_height("300px")
    card1.expect_full_screen_available(True)

    # Test switch1
    switch1 = controller.InputSwitch(page, "switch1")
    switch1.expect_label("Basic switch (default params)")
    switch1.expect_checked(False)  # Test initial value

    # Toggle switch1 and verify
    switch1.set(True)
    switch1.expect_checked(True)

    # Test switch2
    switch2 = controller.InputSwitch(page, "switch2")
    switch2.expect_label("Switch with custom width")
    switch2.expect_checked(True)  # Test initial value
    switch2.expect_width("300px")

    # Toggle switch2 and verify
    switch2.set(False)
    switch2.expect_checked(False)
