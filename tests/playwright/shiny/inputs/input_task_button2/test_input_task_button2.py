from __future__ import annotations

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def click_extended_task_button(
    button: controller.InputTaskButton,
) -> None:
    button.expect_state("ready")
    button.click(timeout=0)
    button.expect_state("busy", timeout=0)
    button.expect_state("ready", timeout=0)


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    controller.OutputText(page, "mod1-text_counter").expect_value(
        "Button clicked 0 times"
    )

    # Extended task
    button_task = controller.InputTaskButton(page, "mod1-btn")
    button_task.expect_label_ready("Go")
    button_task.expect_auto_reset(True)
    click_extended_task_button(button_task)

    controller.OutputText(page, "mod1-text_counter").expect_value(
        "Button clicked 1 times"
    )
