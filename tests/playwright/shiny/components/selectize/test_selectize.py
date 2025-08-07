# import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_selectize(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    selectize_menu = controller.InputSelectize(page, "reprex_selectize-x")
    selectize_menu.expect_choices(["Foo 0", "Foo 1", "Foo 2"])
    selectize_menu.expect_multiple(True)
    selectize_menu.set(["Foo 0", "Foo 1"])
    selectize_menu.expect_selected(["Foo 0", "Foo 1"])
