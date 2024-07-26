from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_basic_error(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")

    controller.OutputCode(page, "message_state").expect.not_to_have_text(
        "",
        timeout=30 * 1000,
    )

    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    chat.set_user_input("Hello!")
    chat.send_user_input()
    chat.expect_latest_message("Hello!", timeout=30 * 1000)

    error_loc = page.locator(".shiny-notification-error")
    expect(error_loc).to_be_visible()
