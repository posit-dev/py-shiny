from __future__ import annotations
from conftest import ShinyAppProc
from controls import InputNumeric, InputTaskButton, OutputText
from playwright.sync_api import Page


def click_extended_task_button(
    button: InputTaskButton,
    current_time: OutputText,
    button_label: list[str],
) -> str:
    button.expect_state("ready")
    button.expect_label_text(button_label)
    button.click(timeout=0)
    button.expect_state("busy", timeout=0)
    return current_time.get_value(timeout=0)


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    y = InputNumeric(page, "y")
    y.set("4")
    result = OutputText(page, "show_result")
    current_time = OutputText(page, "current_time")
    current_time.expect.not_to_be_empty()

    result.expect_value("3")

    # extended task
    button1 = InputTaskButton(page, "btn")
    time1 = click_extended_task_button(
        button1, current_time, button_label=["Compute, slowly", "\n  \n Processing..."]
    )
    current_time.expect.not_to_have_text(time1, timeout=500)

    result.expect_value("3", timeout=0)
    result.expect_value("5", timeout=(3 + 1) * 1000)
    y.set("15")
    result.expect_value("5")

    # extended task with blocking
    button2 = InputTaskButton(page, "btn2")
    time2 = click_extended_task_button(
        button2, current_time, button_label=["Compute 2 slowly", "\n  \n Blocking..."]
    )
    current_time.expect_value(time2, timeout=0)
