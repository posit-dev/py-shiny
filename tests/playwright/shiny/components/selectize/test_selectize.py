# import pytest
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_selectize(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    selectize_menu = controller.InputSelectize(page, "serverside-x")
    selectize_menu.expect_choices(["Foo 0", "Foo 1", "Foo 2"])
    selectize_menu.expect_multiple(True)
    selectize_menu.set(["Foo 0", "Foo 1"])
    selectize_menu.expect_selected(["Foo 0", "Foo 1"])

    selectize_menu2 = controller.InputSelectize(page, "clientside-x")
    selectize_menu2.expect_choices(["Foo 0", "Foo 1", "Foo 2"])
    selectize_menu2.expect_multiple(True)
    selectize_menu2.set(["Foo 0", "Foo 1"])
    selectize_menu2.expect_selected(["Foo 0", "Foo 1"])

    expect(page.locator("css=input")).to_have_count(2)
    expect(page.locator("css=input").first).to_have_attribute("placeholder", "Search")
