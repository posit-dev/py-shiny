from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect._internal import _expect_nav_to_have_header_footer
from shiny.run import ShinyAppProc


def test_navset_hidden_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    navset_hidden_1 = controller.NavsetHidden(page, "hidden_tabs1")
    radio1 = controller.InputRadioButtons(page, "controller1")
    navset_hidden_1.expect_value("panel2")
    navset_hidden_1._expect_content_text("Panel 2 content")
    # assert the DOM structure for hidden_navset with header and footer is preserved
    _expect_nav_to_have_header_footer(
        navset_hidden_1.get_loc_active_content().locator("..").locator(".."),
        "navset_hidden_header1",
        "navset_hidden_footer1",
    )
    # assert header and footer contents
    expect(page.locator("#navset_hidden_header1")).to_contain_text(
        "Navset_hidden_header"
    )
    expect(page.locator("#navset_hidden_footer1")).to_contain_text(
        "Navset_hidden_footer"
    )
    radio1.set("1")
    navset_hidden_1.expect_value("panel1")
    navset_hidden_1._expect_content_text("Panel 1 content")

    navset_hidden_2 = controller.NavsetHidden(page, "hidden_tabs2")
    navset_hidden_2.expect_value("panel4")
