import pytest
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Page begins with 2 tabs: "Hello" and "Foo" and a nav menu with 2 static items.
    controller.NavsetTab(page, "foo-navset").expect_nav_titles(["Panel 1", "Panel 2"])
    controller.NavsetTab(page, "bar-navset").expect_nav_titles(["Panel 1", "Panel 2"])

    # Click hide-tab to hide the Foo tabs
    hidetab = controller.InputActionButton(page, "foo-hideTab")
    hidetab.click()

    # Expect the Foo tabs to be hidden
    navpanel = controller.NavPanel(page, "foo-navset", "Panel 2").loc
    expect(navpanel).to_be_hidden()

    # Expect the bar tabs to not be affected
    navpanel2 = controller.NavPanel(page, "bar-navset", "Panel 2").loc
    expect(navpanel2).to_be_visible()

    # Click show-tab to show the Foo tabs again
    showtab = controller.InputActionButton(page, "foo-showTab")
    showtab.click()

    # Expect the Foo tabs to be visible again
    navpanel2 = controller.NavPanel(page, "foo-navset", "Panel 2").loc
    expect(navpanel2).to_be_visible()
    navpanel3 = controller.NavPanel(page, "bar-navset", "Panel 2").loc
    expect(navpanel3).to_be_visible()

    # Click the remove button to remove the panel 2 in bar
    removeTab = controller.InputActionButton(page, "bar-deleteTabs")
    removeTab.click()
    controller.NavsetTab(page, "bar-navset").expect_nav_titles(["Panel 1"])
    controller.NavsetTab(page, "foo-navset").expect_nav_titles(["Panel 1", "Panel 2"])
