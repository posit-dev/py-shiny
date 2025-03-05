import re

from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_stream_result(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")
    stream_result = controller.OutputCode(page, "stream_result")

    expect(chat.loc).to_be_visible(timeout=10 * 1000)

    chat.send_user_input()

    messages = [
        "Message 0",
        "Message 1",
        "Message 2",
        "Message 3",
        "Message 4",
        "Message 5",
        "Message 6",
        "Message 7",
        "Message 8",
        "Message 9",
    ]
    # Allow for any whitespace between messages
    chat.expect_messages(re.compile(r"\s*".join(messages)), timeout=30 * 1000)

    # Verify that the stream result is as expected
    stream_result.expect.to_contain_text("Message 9")
