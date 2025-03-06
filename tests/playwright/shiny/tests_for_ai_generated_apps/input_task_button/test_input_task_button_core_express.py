from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_task_button_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Get the task button controller
    task_btn = controller.InputTaskButton(page, "task_btn")
    task_status = controller.OutputText(page, "task_status")

    # Test initial state
    task_btn.expect_label("Run Task")
    task_btn.expect_label_busy("Processing...")
    task_btn.expect_state("ready")
    task_status.expect_value("Task hasn't started yet")

    # Click the button and test busy state
    task_btn.click()
    task_btn.expect_state("busy")

    # After task completes, verify new state and status
    task_btn.expect_state("ready", timeout=3000)  # Allow time for the 2-second sleep
    task_status.expect_value("Task has been run 1 times")

    # Test a second click
    task_btn.click()
    task_btn.expect_state("busy")
    task_btn.expect_state("ready", timeout=3000)
    task_status.expect_value("Task has been run 2 times")
