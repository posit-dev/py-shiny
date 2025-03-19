from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_input_select_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic select with simple choices
    select1 = controller.InputSelect(page, "basic")
    select1.expect_label("Basic select")

    basic_select_txt = controller.OutputText(page, "basic_text")
    basic_select_txt.expect_value("Select value: option1")

    mod_select1 = controller.InputSelect(page, "first-module_select")
    mod_select1.expect_label("Module select")
    mod_select_txt = controller.OutputText(page, "first-select_text")
    mod_select_txt.expect_value("Select value: choiceA")

    # Change the basic select value
    select1.set("option2")
    basic_select_txt.expect_value("Select value: option2")

    # Change the module select value
    mod_select1.set("choiceB")
    mod_select_txt.expect_value("Select value: choiceB")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    # Change the basic select value again
    select1.set("option3")
    basic_select_txt.expect_value("Select value: option3")

    # Change the module select value again
    mod_select1.set("choiceC")
    mod_select_txt.expect_value("Select value: choiceC")

    # Reload the page to test bookmark
    page.reload()

    basic_select_txt.expect_value("Select value: option2")

    mod_select_txt.expect_value("Select value: choiceB")
