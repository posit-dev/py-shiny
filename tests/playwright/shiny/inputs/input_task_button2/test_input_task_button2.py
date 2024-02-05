from __future__ import annotations

from conftest import ShinyAppProc
from controls import InputTaskButton, OutputText
from playwright.sync_api import Page


def click_extended_task_button(
    button: InputTaskButton,
) -> None:
    button.expect_state("ready")
    button.click(timeout=0)
    button.expect_state("busy", timeout=0)
    button.expect_state("ready", timeout=0)


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    OutputText(page, "mod1-text_counter").expect_value("Button clicked 0 times")

    # Extended task
    button_task = InputTaskButton(page, "mod1-btn")
    button_task.expect_label_ready("Go")
    button_task.expect_auto_reset(True)
    click_extended_task_button(button_task)

    OutputText(page, "mod1-text_counter").expect_value("Button clicked 1 times")
