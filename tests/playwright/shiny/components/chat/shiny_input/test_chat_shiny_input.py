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

    select = controller.InputSelect(page, "select")
    slider = controller.InputSlider(page, "slider")
    expect(select.loc).to_be_visible(timeout=TIMEOUT)
    expect(slider.loc).to_be_visible(timeout=TIMEOUT)

    chat.expect_latest_message("Now selected: a and 50")

    select.set("b")
    chat.expect_latest_message("Now selected: b and 50")

    slider.set("5")
    chat.expect_latest_message("Now selected: b and 5")
