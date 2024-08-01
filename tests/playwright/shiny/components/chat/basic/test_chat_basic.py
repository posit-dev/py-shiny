from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")

    # Verify starting state
    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    initial_message = "Hello! How can I help you today?"
    chat.expect_latest_message(initial_message, timeout=30 * 1000)

    # Verify user input is empty and input button / enter is disabled
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()
    chat.send_user_input(method="enter")
    chat.expect_latest_message(initial_message)

    # Verify user input can be entered, inserted, sent, and cleared
    user_message = "I need help with something"
    chat.set_user_input(user_message)
    expect(chat.loc_input_button).to_be_enabled()
    chat.expect_latest_message(initial_message)
    chat.send_user_input(method="enter")
    chat.expect_latest_message(f"You said: {user_message}")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()

    # Same as above, but with click instead of enter
    user_message2 = "I need help with something else"
    chat.set_user_input(user_message2)
    chat.send_user_input(method="click")
    chat.expect_latest_message(f"You said: {user_message2}")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()

    # Verify that the message state is as expected
    message_state = controller.OutputCode(page, "message_state")
    message_state_expected = tuple(
        [
            {"content": initial_message, "role": "assistant"},
            {"content": f"\n{user_message}", "role": "user"},
            {"content": f"You said: \n{user_message}", "role": "assistant"},
            {"content": f"{user_message2}", "role": "user"},
            {"content": f"You said: {user_message2}", "role": "assistant"},
        ]
    )
    message_state.expect_value(str(message_state_expected))
