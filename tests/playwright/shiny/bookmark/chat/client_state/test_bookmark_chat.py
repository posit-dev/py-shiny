import re

import pytest
from playwright.sync_api import Page

from shiny.playwright.controller import Chat
from shiny.run import ShinyAppProc


# Up to 5 retries for intermittent WebKit timing issues
@pytest.mark.flaky(reruns=5, reruns_delay=1)
def test_bookmark_chat(page: Page, local_app: ShinyAppProc):

    page.goto(local_app.url)

    assert "?" not in page.url

    chat_controller = Chat(page, "chat")

    chat_controller.expect_messages("Welcome!")

    chat_controller.set_user_input("Testing")
    chat_controller.send_user_input()

    chat_controller.expect_messages("Welcome!\nTesting\nRepeater: Testing")

    page.wait_for_url(re.compile(r".*\?.*"), timeout=30 * 1000)

    page.reload()

    chat_controller.expect_messages("Welcome!\nTesting\nRepeater: Testing")
