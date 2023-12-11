# import pytest
from conftest import ShinyAppProc
from controls import InputRadioButtons, LayoutNavSetHidden
from playwright.sync_api import Page


def test_navset_hidden(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # navset_hidden
    navset_hidden = LayoutNavSetHidden(page, "hidden_tabs")
    input_radio_buttons = InputRadioButtons(page, "controller")
    navset_hidden.expect_nav_values(["panel1", "panel2", "panel3"])
    navset_hidden.expect_content("Panel 1 content")
    input_radio_buttons.set("2")
    input_radio_buttons.expect_choices(["1", "2", "3"])
    navset_hidden.expect_content("Panel 2 content")
