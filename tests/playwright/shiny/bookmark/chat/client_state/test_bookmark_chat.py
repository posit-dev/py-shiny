from playwright.sync_api import Page
import re

from shiny.playwright.controller import Chat
from shiny.run import ShinyAppProc


def test_bookmark_chatlas(page: Page, local_app: ShinyAppProc):

    page.goto(local_app.url)

    assert "?" not in page.url

    chat_controller = Chat(page, "chat")

    chat_controller.expect_messages("Welcome!")

    chat_controller.set_user_input("Testing")
    chat_controller.send_user_input()

    chat_controller.expect_messages("Welcome!\nTesting\nRepeater: Testing")

    page.wait_for_url(re.compile(r".*\?.*"), timeout=2) # Wait up to 2 seconds

    page.reload()

    chat_controller.expect_messages("Welcome!\nTesting\nRepeater: Testing")
