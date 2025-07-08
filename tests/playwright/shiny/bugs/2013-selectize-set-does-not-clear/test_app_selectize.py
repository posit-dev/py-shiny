from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture("app_selectize.py")


def test_inputselectize(page: Page, app: ShinyAppProc):
    page.goto(app.url)

    controller.InputSelectize(page, "test_selectize").set(
        ["Choice 1"]
    )  # Add Choice 1 to selections
    controller.InputSelectize(page, "test_selectize").set(
        ["Choice 1", "Choice 2"]
    )  # Add Choice 2 to selections
    controller.InputSelectize(page, "test_selectize").set([])  # Clear selections
