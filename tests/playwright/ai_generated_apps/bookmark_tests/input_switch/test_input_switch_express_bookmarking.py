from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_switch_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    switch1 = controller.InputSwitch(page, "basic")
    basic_txt = controller.OutputText(page, "basic_text")
    switch2 = controller.InputSwitch(page, "first-module_switch")
    module_txt = controller.OutputText(page, "first-switch_text")

    # Check initial values
    switch1.expect_checked(False)
    basic_txt.expect_value("Switch value: False")
    switch2.expect_checked(False)
    module_txt.expect_value("Switch value: False")

    # Toggle switches
    switch1.set(True)
    switch1.expect_checked(True)

    switch2.set(True)
    switch2.expect_checked(True)

    basic_txt.expect_value("Switch value: True")
    module_txt.expect_value("Switch value: True")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    switch1.set(False)
    switch1.expect_checked(False)
    switch2.set(False)
    switch2.expect_checked(False)

    page.reload()
    basic_txt.expect_value("Switch value: True")
    module_txt.expect_value("Switch value: True")
    switch1.expect_checked(True)
    switch2.expect_checked(True)
