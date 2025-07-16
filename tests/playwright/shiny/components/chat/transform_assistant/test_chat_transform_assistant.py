from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_transform_assistant(page: Page, local_app: ShinyAppProc) -> None:
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
    code = chat.loc_latest_message.locator("code")
    expect(code).to_have_text("hello", timeout=30 * 1000)

    user_msg2 = "return HTML"
    chat.set_user_input(user_msg2)
    chat.send_user_input()
    bold = chat.loc_latest_message.locator("b")
    expect(bold).to_have_text("Transformed response")

    message_state_expected = tuple(
        [
            {"content": "hello", "role": "user"},
            {"content": "hello", "role": "assistant"},
            {"content": "return HTML", "role": "user"},
            {"content": "return HTML", "role": "assistant"},
        ]
    )
    message_state.expect_value(str(message_state_expected))

    message_state_expected2 = tuple(
        [
            {"content": "hello", "role": "user"},
            {"content": "Transformed response: `hello`", "role": "assistant"},
            {"content": "return HTML", "role": "user"},
            {
                "content": "<b>Transformed response</b>: return HTML",
                "role": "assistant",
            },
        ]
    )
    message_state2.expect_value(str(message_state_expected2))
