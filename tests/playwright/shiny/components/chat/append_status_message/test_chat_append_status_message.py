from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chat = controller.Chat(page, "chat")
    content = controller.InputText(page, "content")
    content_is_html = controller.InputSwitch(page, "content_is_html")
    status_type = controller.InputRadioButtons(page, "type")
    submit = controller.InputActionButton(page, "submit")

    # Verify starting state
    expect(chat.loc).to_be_visible(timeout=30 * 1000)
    initial_message = "Hello! How can I help you today?"
    chat.expect_latest_message(initial_message, timeout=30 * 1000)

    # Send a status message
    content.set("Using model <code>llama3.1</code>")
    content_is_html.set(True)
    status_type.set("dynamic")
    submit.click()
    chat.expect_latest_message("Using model llama3.1")
    expect(chat.loc_latest_message).to_have_attribute("content_type", "html")
    expect(chat.loc_latest_message).to_have_attribute("type", "dynamic")


    # Send a status message that updates the original message
    content.set("Using model <code>phi4</code>")
    submit.click()
    chat.expect_latest_message("Using model phi4")
    expect(chat.loc_latest_message).to_have_attribute("content_type", "html")
    expect(chat.loc_latest_message).to_have_attribute("type", "dynamic")


    # Send a new status message that is static (doesn't overwrite previous message)
    html_message='<div class="alert alert-warning">Lost connection with provider.</div>'
    content.set(html_message)
    status_type.set("static")
    submit.click()
    chat.expect_latest_message("Lost connection with provider.")
    expect(chat.loc_latest_message).to_have_attribute("content_type", "html")
    expect(chat.loc_latest_message).to_have_attribute("type", "static")
    expect(chat.loc_latest_message.locator("> :first-child")).to_have_class("alert alert-warning")
    # previous status message is still there
    expect(chat.loc_messages.locator("> :nth-last-child(2)")).to_have_text("Using model phi4")

    # Now another message as raw text
    content.set("Using model <code>deepseek-r1</code>")
    status_type.set("dynamic")
    content_is_html.set(False)
    submit.click()
    chat.expect_latest_message("Using model <code>deepseek-r1</code>")
    expect(chat.loc_latest_message).to_have_attribute("content_type", "text")
    expect(chat.loc_latest_message).to_have_attribute("type", "dynamic")

    # Overwrite this message with one with raw html
    content_is_html.set(True)
    submit.click()
    chat.expect_latest_message("Using model deepseek-r1")
    expect(chat.loc_latest_message).to_have_attribute("content_type", "html")
    expect(chat.loc_latest_message).to_have_attribute("type", "dynamic")


    chat.set_user_input("Hello")
    chat.send_user_input()
    chat.expect_latest_message("You said: Hello")
    content.set("Disconnecting. <strong>Goodbye!</strong>")
    submit.click()
    chat.expect_latest_message("Disconnecting. Goodbye!")
    expect(chat.loc_latest_message).to_have_attribute("content_type", "html")
    expect(chat.loc_latest_message).to_have_attribute("type", "dynamic")
    expect(chat.loc_messages.locator("> :nth-last-child(4)")).to_have_text("Using model deepseek-r1")
