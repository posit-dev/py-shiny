from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_validate_chat_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")
    expect(chat.loc).to_be_visible()

    chat.set_user_input("Hello!")
    chat.send_user_input()
    chat.expect_latest_message("Hello!")

    error_loc = page.locator(".shiny-notification-error")
    expect(error_loc).to_be_visible()
