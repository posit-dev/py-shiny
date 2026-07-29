import re
from pathlib import Path

import pytest
from playwright.sync_api import Page

from shiny.playwright.controller import Chat
from shiny.run import ShinyAppProc, run_shiny_app


# `app.py` uses `bookmark_store="url"`, `app-server.py` uses `"server"`. Both are
# worth covering: `ui.Chat` renders its initial messages from an `on_restore`
# callback, and the two stores reach that callback by different paths -- `"url"`
# decodes the query string, while `"server"` has no `_state_id_` at all on a plain
# page load.
@pytest.mark.parametrize("app_name", ["app.py", "app-server.py"])
# Up to 5 retries for intermittent WebKit timing issues
@pytest.mark.flaky(reruns=5, reruns_delay=1)
def test_bookmark_chat(page: Page, app_name: str):

    app: ShinyAppProc = run_shiny_app(
        Path(__file__).parent / app_name,
        wait_for_start=True,
    )

    try:
        page.goto(app.url)

        assert "?" not in page.url

        chat_controller = Chat(page, "chat")

        chat_controller.expect_messages("Welcome!")

        chat_controller.set_user_input("Testing")
        chat_controller.send_user_input()

        chat_controller.expect_messages("Welcome!\nTesting\nRepeater: Testing")

        page.wait_for_url(re.compile(r".*\?.*"), timeout=30 * 1000)

        page.reload()

        chat_controller.expect_messages("Welcome!\nTesting\nRepeater: Testing")

    finally:
        app.close()
