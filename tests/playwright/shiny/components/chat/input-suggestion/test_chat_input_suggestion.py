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
    first = chat.loc.locator("#first", has_text="1st input suggestion")
    second = chat.loc.locator("#second")
    third = chat.loc.locator("#third")
    fourth = chat.loc.locator("#fourth")
    fifth = chat.loc.locator("#fifth")

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

    # Test auto-submitting suggestions
    fourth.click()
    chat.expect_latest_message("You said: this suggestion will auto-submit")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()
    expect(chat.loc_input).not_to_be_focused()

    fifth.focus()
    page.keyboard.press("Enter")
    chat.expect_latest_message("You said: another suggestion")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()
    expect(chat.loc_input).not_to_be_focused()

    # Reset chat
    chat.set_user_input("reset")
    chat.send_user_input()
    chat.expect_latest_message("You said: reset")

    # Test keyboard modifiers - Alt + event = set but do not submit
    fourth.click(modifiers=["Alt"])
    chat.expect_user_input("this suggestion will auto-submit")
    chat.expect_latest_message("You said: reset")

    fifth.focus()
    page.keyboard.press("Alt+Enter")
    chat.expect_user_input("another suggestion")
    chat.expect_latest_message("You said: reset")

    # Reset chat
    chat.send_user_input()
    chat.expect_user_input("")

    # Test keyboard modifiers - Cmd/Ctrl + event = submit the suggestion
    first.click(modifiers=["ControlOrMeta"])
    chat.expect_latest_message("You said: 1st input suggestion")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()
    expect(chat.loc_input).not_to_be_focused()

    second.focus()
    page.keyboard.press("ControlOrMeta+Enter")
    chat.expect_latest_message("You said: The actual suggestion")
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()
    expect(chat.loc_input).not_to_be_focused()
