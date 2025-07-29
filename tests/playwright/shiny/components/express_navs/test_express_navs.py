import pytest
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Page begins with 2 tabs: "Panel 1" and "Panel 2"
    controller.NavsetTab(page, "foo-navset").expect_nav_titles(["Panel 1", "Panel 2"])
    controller.NavsetTab(page, "bar-navset").expect_nav_titles(["Panel 1", "Panel 2"])

    # Click hide-tab to hide Panel 2 in the foo navset
    hidetab = controller.InputActionButton(page, "foo-hide_tab")
    hidetab.click()

    # Expect the Foo's Panel 2 to be hidden
    navpanel = controller.NavPanel(page, "foo-navset", "Panel 2").loc
    expect(navpanel).to_be_hidden()

    # Expect the bar Panel 2 tab to not be affected
    navpanel2 = controller.NavPanel(page, "bar-navset", "Panel 2").loc
    expect(navpanel2).to_be_visible()

    # Click show-tab to show the foo Panel 2 tab again
    showtab = controller.InputActionButton(page, "foo-show_tab")
    showtab.click()

    # Expect the Foo Panel 2 tab to be visible again as well as the bar Panel 2
    navpanel2 = controller.NavPanel(page, "foo-navset", "Panel 2").loc
    expect(navpanel2).to_be_visible()
    navpanel3 = controller.NavPanel(page, "bar-navset", "Panel 2").loc
    expect(navpanel3).to_be_visible()

    # Click the remove button to remove the panel 2 in bar
    removeTab = controller.InputActionButton(page, "bar-delete_tabs")
    removeTab.click()

    # Check that bar's Panel 2 is gone, but foo's Panel 2 is unaffected
    controller.NavsetTab(page, "bar-navset").expect_nav_titles(["Panel 1"])
    controller.NavsetTab(page, "foo-navset").expect_nav_titles(["Panel 1", "Panel 2"])
