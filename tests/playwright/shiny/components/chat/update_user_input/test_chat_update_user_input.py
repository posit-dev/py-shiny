from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_update_user_input(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")

    # Starting state sanity check
    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    chat.expect_user_input("")
    expect(chat.loc_input_button).to_be_disabled()

    # Locate action buttons
    set_input = controller.InputActionButton(page, "set_input")
    set_and_focus = controller.InputActionButton(page, "set_and_focus")
    submit = controller.InputActionButton(page, "submit")
    submit_and_focus = controller.InputActionButton(page, "submit_and_focus")

    # Just set the input ----
    set_input.loc.focus()
    set_input.click()
    chat.expect_user_input("Input was set, but neither focused nor submitted.")
    expect(chat.loc_input_button).to_be_enabled()
    expect(chat.loc_input).not_to_be_focused()

    # Set the input and move focus ----
    set_and_focus.click()
    set_msg = "Input was set and focused, but not submitted."
    chat.expect_user_input(set_msg)
    expect(chat.loc_input_button).to_be_enabled()
    expect(chat.loc_input).to_be_focused()

    # Auto submit ----
    submit.loc.focus()
    submit.click()
    chat.expect_user_input(set_msg)  # User doesn't lose what they had written
    chat.expect_latest_message("You said: This chat was sent on behalf of the user.")
    expect(chat.loc_input_button).to_be_enabled()
    expect(chat.loc_input).not_to_be_focused()

    # Input remains cleared if previously clear (have to clear the input first)
    chat.loc_input.focus()
    while chat.loc_input.input_value():
        chat.loc_input.press("Backspace")

    chat.expect_user_input("")

    submit.loc.focus()
    submit.click()
    chat.expect_user_input("")
    chat.expect_latest_message("You said: This chat was sent on behalf of the user.")
    expect(chat.loc_input_button).to_be_disabled()
    expect(chat.loc_input).not_to_be_focused()

    # Auto submit and move focus ----
    submit_and_focus.loc.focus()
    submit_and_focus.click()
    chat.expect_user_input("")
    chat.expect_latest_message(
        "You said: This chat was sent on behalf of the user. Input will still be focused."
    )
    expect(chat.loc_input_button).to_be_disabled()
    expect(chat.loc_input).to_be_focused()
