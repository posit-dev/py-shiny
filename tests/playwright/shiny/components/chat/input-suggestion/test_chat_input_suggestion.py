from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_input_suggestion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")

    # Starting state sanity check
    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()

    # Locate input suggestions
    first = chat.loc.locator(".chat-input-suggestion", has_text="1st input suggestion")
    second = chat.loc.locator("span[data-input-suggestion]")
    third = chat.loc.locator("img[data-input-suggestion]")

    # Click on each suggestion and verify the input
    first.click()
    chat.expect_user_input("1st input suggestion")

    second.click()
    chat.expect_user_input("The actual suggestion")

    third.click()
    chat.expect_user_input("A 3rd, image-based, suggestion")

    # Verify input button / enter is enabled
    expect(chat.loc_input_button).to_be_enabled()

    # Submit the input
    chat.send_user_input(method="click")
    chat.expect_latest_message("You said: A 3rd, image-based, suggestion")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()
