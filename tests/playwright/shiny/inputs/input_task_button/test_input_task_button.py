from __future__ import annotations

import time

from conftest import ShinyAppProc
from controls import InputNumeric, InputTaskButton, OutputText
from playwright.sync_api import Page


def click_extended_task_button(
    button: InputTaskButton,
    current_time: OutputText,
) -> str:
    button.expect_state("ready")
    button.click(timeout=0)
    button.expect_state("busy", timeout=0)
    return current_time.get_value(timeout=0)


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    y = InputNumeric(page, "y")
    y.set("4")
    result = OutputText(page, "show_result")
    current_time = OutputText(page, "current_time")
    # Make sure the time has content
    current_time.expect.not_to_be_empty()

    # Wait until shiny is stable
    result.expect_value("3")

    # Extended task
    button_task = InputTaskButton(page, "btn_task")
    button_task.expect_label_busy("\n  \n Processing...")
    button_task.expect_label_ready("Non-blocking task")
    button_task.expect_auto_reset(True)
    # Click button and collect the current time from the app
    time1 = click_extended_task_button(
        button_task,
        current_time,
    )
    # Make sure time value updates (before the calculation finishes
    current_time.expect.not_to_have_text(time1, timeout=500)
    result.expect_value("3", timeout=0)
    # After the calculation time plus a buffer, make sure the calculation finishes
    result.expect_value("5", timeout=(1.5 + 1) * 1000)

    # set up Blocking test
    y.set("15")
    result.expect_value("5")

    # Blocking verification
    button_block = InputTaskButton(page, "btn_block")
    button_block.expect_label_busy("\n  \n Blocking...")
    button_block.expect_label_ready("Block compute")
    button_block.expect_auto_reset(True)
    time_block = click_extended_task_button(
        button_block,
        current_time,
    )
    # Make sure time value has not changed after 500ms has ellapsed
    time.sleep(0.5)
    current_time.expect_value(time_block, timeout=0)
