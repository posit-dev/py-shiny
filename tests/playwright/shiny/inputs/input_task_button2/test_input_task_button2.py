from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    controller.OutputText(page, "mod1-text_counter").expect_value(
        "Button clicked 0 times"
    )

    button_task = controller.InputTaskButton(page, "mod1-btn")
    button_task.expect_label_ready("Go")
    button_task.expect_auto_reset(True)

    # The app holds the button's click handler (and therefore its "busy"
    # state) until this file exists, so the busy assertion below cannot miss
    # the busy window, no matter how slowly the test executes.
    release_file = Path(controller.OutputText(page, "mod1-release_file").get_value())

    button_task.expect_state("ready")
    button_task.click()
    button_task.expect_state("busy")
    release_file.touch()
    button_task.expect_state("ready", timeout=10 * 1000)

    controller.OutputText(page, "mod1-text_counter").expect_value(
        "Button clicked 1 times"
    )
