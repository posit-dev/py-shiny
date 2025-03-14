from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_inject(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    TIMEOUT = 30 * 1000

    chat = controller.Chat(page, "chat")
    expect(chat.loc).to_be_visible(timeout=TIMEOUT)

    basic_stream = controller.InputActionButton(page, "basic_stream")
    expect(basic_stream.loc).to_be_visible(timeout=TIMEOUT)
    basic_stream.click()

    # TODO: how to test the progress messages?
    chat.expect_latest_message(
        "Completed stream 1 ✅",
        timeout=TIMEOUT,
    )

    chat.set_user_input("Hello")
    chat.send_user_input()
    chat.expect_latest_message("You said: Hello", timeout=TIMEOUT)

    nested_stream = controller.InputActionButton(page, "nested_stream")
    expect(nested_stream.loc).to_be_visible(timeout=TIMEOUT)
    nested_stream.click()

    # TODO: how to test the progress messages?
    chat.expect_latest_message(
        "Starting outer stream...\n\nCompleted inner stream ✅\n\n...outer stream complete",
        timeout=TIMEOUT,
    )

    chat.set_user_input("Hello")
    chat.send_user_input()
    chat.expect_latest_message("You said: Hello", timeout=TIMEOUT)

    # TODO: test message state
    # message_state = controller.OutputCode(page, "message_state")
