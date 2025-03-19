from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py"])


def test_bookmark_exclusion(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    mod1_text_box = controller.InputText(page, "mod1-text_in")
    mod1_txt = controller.OutputText(page, "mod1-included_module_text")
    mod1_txt.expect_value("Included text:")

    mod1_num = controller.InputNumeric(page, "mod1-num_in")
    mod1_num_txt = controller.OutputText(page, "mod1-included_module_num")
    mod1_num_txt.expect_value("Included num: 1")

    mod1_excluded = controller.InputText(page, "mod1-text_excl")
    mod1_excluded_txt = controller.OutputText(page, "mod1-excluded_module_text")
    mod1_excluded_txt.expect_value("Excluded text:")

    mod1_text_box.set("Hello world")
    mod1_txt.expect_value("Included text: Hello world")
    mod1_num.set("10")
    mod1_num_txt.expect_value("Included num: 10")
    mod1_excluded.set("Hello excluded")
    mod1_excluded_txt.expect_value("Excluded text: Hello excluded")

    # reload page
    page.reload()

    mod1_txt.expect_value("Included text: Hello world")
    mod1_num_txt.expect_value("Included num: 10")
    mod1_excluded_txt.expect_value("Excluded text:")
