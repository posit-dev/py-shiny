from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_transform(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")
    message_state = controller.OutputCode(page, "message_state")
    message_state2 = controller.OutputCode(page, "message_state2")

    # Wait for app to load
    message_state.expect_value("()", timeout=30 * 1000)

    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    expect(chat.loc_input_button).to_be_disabled()

    user_msg = "hello"
    chat.set_user_input(user_msg)
    chat.send_user_input()
    chat.expect_latest_message(
        f"Transformed input: {user_msg.upper()}",
        timeout=30 * 1000,
    )

    user_msg2 = "return None"
    chat.set_user_input(user_msg2)
    chat.send_user_input()
    chat.expect_latest_message("return None")

    user_msg3 = "return custom message"
    chat.set_user_input(user_msg3)
    chat.send_user_input()
    chat.expect_latest_message("Custom message")

    message_state_expected = tuple(
        [
            {"content": user_msg.upper(), "role": "user"},
            {"content": f"Transformed input: {user_msg.upper()}", "role": "assistant"},
            {"content": "return None", "role": "user"},
            {"content": "return custom message", "role": "user"},
            {"content": "Custom message", "role": "assistant"},
        ]
    )
    message_state.expect_value(str(message_state_expected))

    message_state_expected2 = tuple(
        [
            {"content": user_msg, "role": "user"},
            {"content": f"Transformed input: {user_msg.upper()}", "role": "assistant"},
            {"content": "return None", "role": "user"},
            {"content": "return custom message", "role": "user"},
            {"content": "Custom message", "role": "assistant"},
        ]
    )
    message_state2.expect_value(str(message_state_expected2))
