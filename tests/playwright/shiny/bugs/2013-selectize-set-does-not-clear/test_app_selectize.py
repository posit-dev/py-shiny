from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture("app_selectize.py")


def test_inputselectize(page: Page, app: ShinyAppProc):
    page.goto(app.url)

    input_selectize = controller.InputSelectize(page, "test_selectize")
    output_text = controller.OutputText(page, "test_selectize_output")

    input_selectize.set(["Choice 1", "Choice 2", "Choice 3"])
    output_text.expect_value("Selected: Choice 1, Choice 2, Choice 3")
    input_selectize.set(["Choice 2", "Choice 3"])
    output_text.expect_value("Selected: Choice 2, Choice 3")
    input_selectize.set(["Choice 3"])
    output_text.expect_value("Selected: Choice 3")
    input_selectize.set([])
    output_text.expect_value("Selected: ")
