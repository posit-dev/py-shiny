from __future__ import annotations

import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def click_extended_task_button(
    button: controller.InputTaskButton,
    current_time: controller.OutputText,
) -> str:
    button.expect_state("ready")
    button.click()
    # The "busy" state only lasts as long as the server-side task (~1.5s), so
    # this assertion must run promptly; a finite timeout keeps a missed busy
    # window a fast, diagnosable failure instead of an infinite hang.
    button.expect_state("busy")
    return current_time.get_value()


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    y = controller.InputNumeric(page, "y")
    y.set("4")
    result = controller.OutputText(page, "show_result")
    current_time = controller.OutputText(page, "current_time")
    # Make sure the time has content
    current_time.expect.not_to_be_empty()

    # Wait until shiny is stable
    result.expect_value("3")

    # Extended task
    button_task = controller.InputTaskButton(page, "btn_task")
    button_task.expect_label_busy("\n  \n Processing...")
    button_task.expect_label_ready("Non-blocking task")
    button_task.expect_auto_reset(True)
    # Click button and collect the current time from the app
    time1 = click_extended_task_button(
        button_task,
        current_time,
    )
    # Make sure time value updates (before the 1.5s calculation finishes)
    current_time.expect.not_to_have_text(time1, timeout=1000)
    result.expect_value("3")
    # After the calculation time plus a buffer, make sure the calculation finishes
    result.expect_value("5", timeout=10 * 1000)

    # Negative control for the render counter used by the blocking check
    # below: the session keeps flushing during an extended task, so the second
    # (clicked) non-blocking window must contain renders. This proves a zero
    # count means "blocked", not "counter broken". The first (startup) window
    # overlaps the startup blocking window, so its count is not constrained.
    renders_during_nonblock = controller.OutputText(page, "renders_during_nonblock")
    renders_during_nonblock.expect_value(re.compile(r"^\d+,[1-9]\d*$"))

    # set up Blocking test
    y.set("15")
    result.expect_value("5")

    # Blocking verification. The server records how many current_time renders
    # occur inside each blocking window; this avoids sampling the display on a
    # timer from the client, which races against in-flight output updates.
    renders_during_block = controller.OutputText(page, "renders_during_block")
    # The `ignore_none=False` handler already ran one blocking window at
    # startup; it must not have allowed any renders either.
    renders_during_block.expect_value("0")

    button_block = controller.InputTaskButton(page, "btn_block")
    button_block.expect_label_busy("\n  \n Blocking...")
    button_block.expect_label_ready("Block compute")
    button_block.expect_auto_reset(True)
    click_extended_task_button(
        button_block,
        current_time,
    )
    # Once the blocking computation finishes, the server reports zero
    # current_time renders inside the second blocking window.
    renders_during_block.expect_value("0,0", timeout=10 * 1000)
    # The time ticker must still be alive afterwards, proving the zero count
    # came from blocking rather than from a dead ticker.
    current_time.expect.not_to_have_text(current_time.get_value(), timeout=1000)
