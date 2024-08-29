from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_transform_assistant(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")
    message_state = controller.OutputCode(page, "message_state")

    # Wait for app to load
    message_state.expect_value("()", timeout=30 * 1000)

    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    expect(chat.loc_input_button).to_be_disabled()

    chat.set_user_input("foo")
    chat.send_user_input()
    chat.expect_latest_message("Simple response...DONE!", timeout=30 * 1000)

    message_state_expected = tuple(
        [
            {"content": "foo", "role": "user"},
            {"content": "Simple response", "role": "assistant"},
        ]
    )
    message_state.expect_value(str(message_state_expected))
