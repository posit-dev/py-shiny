from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_message_stream_context(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    TIMEOUT = 30 * 1000

    chat = controller.Chat(page, "chat")
    expect(chat.loc).to_be_visible(timeout=TIMEOUT)

    stream_1 = controller.InputActionButton(page, "stream_1")
    expect(stream_1.loc).to_be_visible(timeout=TIMEOUT)
    stream_1.click()

    chat.expect_latest_message("Basic stream", timeout=TIMEOUT)

    stream_2 = controller.InputActionButton(page, "stream_2")
    expect(stream_2.loc).to_be_visible(timeout=TIMEOUT)
    stream_2.click()

    chat.expect_latest_message("Finished", timeout=TIMEOUT)

    chat.set_user_input("Hello")
    chat.send_user_input()
    chat.expect_latest_message("You said: Hello", timeout=TIMEOUT)

    stream_3 = controller.InputActionButton(page, "stream_3")
    expect(stream_3.loc).to_be_visible(timeout=TIMEOUT)
    stream_3.click()

    chat.expect_latest_message(
        "Outer startInner startInner endOuter end",
        timeout=TIMEOUT,
    )

    stream_4 = controller.InputActionButton(page, "stream_4")
    expect(stream_4.loc).to_be_visible(timeout=TIMEOUT)
    stream_4.click()

    chat.expect_latest_message(
        "Outer startInner endOuter end",
        timeout=TIMEOUT,
    )

    stream_5 = controller.InputActionButton(page, "stream_5")
    expect(stream_5.loc).to_be_visible(timeout=TIMEOUT)
    stream_5.click()

    chat.expect_latest_message(
        "Inner startInner endOuter end",
        timeout=TIMEOUT,
    )

    stream_6 = controller.InputActionButton(page, "stream_6")
    expect(stream_6.loc).to_be_visible(timeout=TIMEOUT)
    stream_6.click()

    chat.expect_latest_message(
        "Outer startInner endOuter end",
        timeout=TIMEOUT,
    )

    chat.set_user_input("Goodbye")
    chat.send_user_input()
    chat.expect_latest_message("You said: Goodbye", timeout=TIMEOUT)

    # Test server-side message state
    message_state = controller.OutputCode(page, "message_state")
    message_state_expected = tuple(
        [
            {"content": "Basic stream", "role": "assistant"},
            {"content": "Finished", "role": "assistant"},
            {"content": "Hello", "role": "user"},
            {"content": "You said: Hello", "role": "assistant"},
            {
                "content": "Outer startInner startInner endOuter end",
                "role": "assistant",
            },
            {"content": "Outer startInner endOuter end", "role": "assistant"},
            {"content": "Inner startInner endOuter end", "role": "assistant"},
            {"content": "Outer startInner endOuter end", "role": "assistant"},
            {"content": "Goodbye", "role": "user"},
            {"content": "You said: Goodbye", "role": "assistant"},
        ]
    )
    message_state.expect_value(str(message_state_expected))
