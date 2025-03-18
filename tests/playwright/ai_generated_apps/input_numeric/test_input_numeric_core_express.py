from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_numeric_inputs(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic numeric input
    basic = controller.InputNumeric(page, "basic")
    basic_output = controller.OutputText(page, "basic_value")

    basic.expect_label("Basic numeric input")
    basic.expect_value("10")
    basic_output.expect_value("Current value: 10")

    # Test with new value
    basic.set("20")
    basic_output.expect_value("Current value: 20")

    # Test numeric input with min/max
    with_min_max = controller.InputNumeric(page, "with_min_max")
    minmax_output = controller.OutputText(page, "minmax_value")

    with_min_max.expect_label("With min and max values")
    with_min_max.expect_value("5")
    with_min_max.expect_min("0")
    with_min_max.expect_max("10")
    minmax_output.expect_value("Current value: 5")

    # Test with step size
    with_step = controller.InputNumeric(page, "with_step")
    step_output = controller.OutputText(page, "step_value")

    with_step.expect_label("With step size")
    with_step.expect_value("0")
    with_step.expect_min("0")
    with_step.expect_max("100")
    with_step.expect_step("5")
    step_output.expect_value("Current value: 0")

    # Test with custom width
    with_width = controller.InputNumeric(page, "with_width")
    width_output = controller.OutputText(page, "width_value")

    with_width.expect_label("With custom width")
    with_width.expect_value("42")
    with_width.expect_width("200px")
    width_output.expect_value("Current value: 42")
