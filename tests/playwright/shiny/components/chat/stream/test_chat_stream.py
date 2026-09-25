from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")
    message_state = controller.OutputCode(page, "message_state")

    # Wait for app to load
    message_state.expect.not_to_have_text("", timeout=30 * 1000)

    expect(chat.loc).to_be_visible()
    expect(chat.loc_input_button).to_be_disabled()

    messages = [
        "FIRST FIRST FIRST",
        "SECOND SECOND SECOND",
        "THIRD THIRD THIRD",
        "FOURTH FOURTH FOURTH",
        "FIFTH FIFTH FIFTH",
    ]
    # TODO: Once https://github.com/posit-dev/shinychat/issues/417 is fixed, assert
    # the messages appear in call order (FIRST..FIFTH). Effects run concurrently, so
    # a streamed message can currently land after one appended later.
    for message in messages:
        expect(chat.loc_messages).to_contain_text(message)
        message_state.expect.to_contain_text(
            str({"content": message, "role": "assistant"})
        )
