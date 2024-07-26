from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_validate_chat_append_user_message(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")

    # Verify starting state
    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    chat.expect_latest_message("A user message", timeout=30 * 1000)

    # Verify that the message state is as expected
    message_state = controller.OutputCode(page, "message_state")
    message_state_expected = ({"content": "A user message", "role": "user"},)
    message_state.expect_value(str(message_state_expected))
