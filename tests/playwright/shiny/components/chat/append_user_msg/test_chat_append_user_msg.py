from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_validate_chat_append_user_message(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")

    # Verify starting state
    expect(chat.loc).to_be_visible()
    expect(chat.loc_messages).to_be_visible()
    expect(chat.loc_messages).to_have_count(1)
    html = chat.loc_messages.locator("> *").inner_html()
    assert "A user message" in html
    # chat.expect_latest_message("A user message")

    # Verify that the message state is as expected
    message_state = controller.OutputCode(page, "message_state")
    message_state_expected = ({"content": "A user message", "role": "user"},)
    message_state.expect_value(str(message_state_expected))
