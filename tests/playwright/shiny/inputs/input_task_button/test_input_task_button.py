import re
import time
from datetime import datetime

from conftest import ShinyAppProc
from controls import InputTaskButton, OutputText, InputNumeric
from playwright.sync_api import Page


def click_button_and_assert_time_difference(
    button: InputTaskButton,
    current_time: OutputText,
    button_label: list[str],
) -> float:
    button.expect_state("ready")
    button.expect_label_text(button_label)
    time1 = current_time.get_value()
    button.click()
    time.sleep(1.5)
    button.expect_state("busy")
    time2 = current_time.get_value()
    original_time = datetime.strptime(time1, "%H:%M:%S")
    new_time = datetime.strptime(time2, "%H:%M:%S")
    time_difference = new_time - original_time
    time_difference_seconds = time_difference.total_seconds()
    return time_difference_seconds


def test_input_action_task_button(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    y = InputNumeric(page, "y")
    y.set("4")
    result = OutputText(page, "show_result")
    current_time = OutputText(page, "current_time")
    current_time.expect_value(re.compile(r"\d{2}:\d{2}:\d{2}"))

    # extended task
    button1 = InputTaskButton(page, "btn")
    time_diff = click_button_and_assert_time_difference(button1, current_time, button_label=["Compute, slowly", "\n  \n Processing..."])
    assert time_diff > 1

    time.sleep(2)
    assert int(result.get_value()) == 5

    # extended task with blocking
    button2 = InputTaskButton(page, "btn2")
    time_diff = click_button_and_assert_time_difference(button2, current_time, button_label=["Compute 2 slowly", "\n  \n Blocking..."])
    assert time_diff < 1
