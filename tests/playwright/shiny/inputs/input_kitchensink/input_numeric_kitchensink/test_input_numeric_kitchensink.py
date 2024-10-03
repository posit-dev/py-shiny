from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_numeric_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputNumeric(page, "default")
    default.expect_label("Default numeric input")
    default.expect_value("10")
    controller.OutputUi(page, "default_txt").expect.to_have_text("10")

    min_max = controller.InputNumeric(page, "min_max")
    min_max.expect_max("100")
    min_max.expect_min("0")
    min_max.expect_value("50")
    controller.OutputUi(page, "min_max_txt").expect.to_have_text("50")

    step = controller.InputNumeric(page, "step")
    step.expect_step("0.5")

    width = controller.InputNumeric(page, "width")
    width.expect_width("200px")
    width.set("20")
    width.expect_value("20")
    controller.OutputUi(page, "width_txt").expect.to_have_text("20")
