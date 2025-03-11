from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_shiny_output(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    TIMEOUT = 30 * 1000

    chat = controller.Chat(page, "chat")
    expect(chat.loc).to_be_visible(timeout=TIMEOUT)
    expect(chat.loc).to_have_css("color", "rgb(41, 70, 91)")

    select = controller.InputSelect(page, "select")
    toggle = controller.InputSwitch(page, "toggle")
    expect(select.loc).to_be_visible(timeout=TIMEOUT)
    expect(toggle.loc).to_be_visible(timeout=TIMEOUT)

    chat.expect_latest_message("Now selected: a and False")

    select.set("b")
    chat.expect_latest_message("Now selected: b and False")

    toggle.set(True)
    chat.expect_latest_message("Now selected: b and True")

    btn = controller.InputActionButton(page, "insert_input")
    expect(btn.loc).to_be_visible(timeout=TIMEOUT)
    btn.click()

    numeric = controller.InputNumeric(page, "numeric")
    expect(numeric.loc).to_be_visible(timeout=TIMEOUT)
    numeric.set("42")

    chat.expect_latest_message("Numeric value: 42")
