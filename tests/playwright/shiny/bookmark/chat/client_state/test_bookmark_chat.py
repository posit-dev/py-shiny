import re
from pathlib import Path

import pytest
from playwright.sync_api import Page
from utils.deploy_utils import skip_if_shinychat_older_than

from shiny.playwright.controller import Chat
from shiny.run import ShinyAppProc, run_shiny_app


# TODO: cover shinychat's `history=` feature directly rather than the ad hoc
# `RepeaterClient` get_state/set_state plumbing these apps hand-roll.
# `Chat(history=HistoryOptions(...))` now owns conversation persistence --
# including a `restore_mode="bookmark"` that participates in Shiny bookmarking --
# so what is under test here is a path apps should no longer need to write.
# See https://github.com/posit-dev/py-shiny/issues/2489.
#
# `app.py` uses `bookmark_store="url"`, `app-server.py` uses `"server"`. Both are
# worth covering: `ui.Chat` restores its greeting and messages from an `on_restore`
# callback, and the two stores reach that callback by different paths -- `"url"`
# decodes the query string, while `"server"` has no `_state_id_` at all on a plain
# page load.
@pytest.mark.parametrize("app_name", ["app.py", "app-server.py"])
# Up to 5 retries for intermittent WebKit timing issues
@pytest.mark.flaky(reruns=5, reruns_delay=1)
@skip_if_shinychat_older_than("0.7.0")
def test_bookmark_chat(page: Page, app_name: str):

    app: ShinyAppProc = run_shiny_app(
        Path(__file__).parent / app_name,
        wait_for_start=True,
    )

    try:
        page.goto(app.url)

        assert "?" not in page.url

        chat_controller = Chat(page, "chat")

        # No longer relevant: the startup message is a `greeting=` now, and shinychat
        # renders a greeting outside the message list, so it is never part of
        # `expect_messages()`. Asserted via `expect_greeting()` below instead.
        # chat_controller.expect_messages("Welcome!")
        chat_controller.expect_greeting("Welcome!")

        chat_controller.set_user_input("Testing")
        chat_controller.send_user_input()

        chat_controller.expect_messages("Testing\nRepeater: Testing")

        page.wait_for_url(re.compile(r".*\?.*"), timeout=30 * 1000)

        page.reload()

        # Not `expect_greeting()` here: shinychat only renders the greeting while the
        # conversation is empty, so once the restored messages land it is gone.
        chat_controller.expect_messages("Testing\nRepeater: Testing")

    finally:
        app.close()
