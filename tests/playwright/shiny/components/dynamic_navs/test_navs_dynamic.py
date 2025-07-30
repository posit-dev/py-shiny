# import pytest
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # String insertion as panels worked correctly
    page.get_by_role("button", name="Menu", exact=True).click()
    expect(page.get_by_text("Stringier Panel")).to_be_visible()
    page.get_by_role("button", name="Menu", exact=True).click()

    # Page begins with 2 tabs: "Hello" and "Foo" and a nav menu with 2 static items.
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Foo", "Static1", "Static2"]
    )

    # Click add-foo to add a new Foo tab
    addfoo = controller.InputActionButton(page, "add_foo")
    addfoo.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Foo", "Foo-1", "Static1", "Static2"]
    )
    # Check that Foo-1 tab is added
    expect(controller.NavPanel(page, "tabs", "Foo-1").loc).to_be_visible()

    # Click hide-tab to hide the Foo tabs
    hidetab = controller.InputActionButton(page, "hide_tab")
    hidetab.click()

    # Expect the Foo tab to be hidden
    navpanel = controller.NavPanel(page, "tabs", "Foo").loc
    expect(navpanel).to_be_hidden()
    navpanel = controller.NavPanel(page, "tabs", "Foo-1").loc
    expect(navpanel).to_be_visible()

    # Click show-tab to show the Foo tabs again
    showtab = controller.InputActionButton(page, "show_tab")
    showtab.click()

    # Expect the Foo tabs to be visible again
    navpanel2 = controller.NavPanel(page, "tabs", "Foo").loc
    expect(navpanel2).to_be_visible()
    navpanel3 = controller.NavPanel(page, "tabs", "Foo-1").loc
    expect(navpanel3).to_be_visible()

    # Click remove-foo to remove the Foo tab
    removefoo = controller.InputActionButton(page, "remove_foo")
    removefoo.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Foo-1", "Static1", "Static2"]
    )

    # Click add to add a dynamic tab
    add = controller.InputActionButton(page, "add")
    add.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Foo-1", "Static1", "Dynamic-1", "Static2"]
    )

    # Click add again to add another dynamic tab
    add.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Foo-1", "Static1", "Dynamic-1", "Dynamic-2", "Static2"]
    )

    page.get_by_role("button", name="Menu", exact=True).click()

    # Expect static tabs to be visible
    navpanel3 = controller.NavPanel(page, "tabs", "s1").loc
    expect(navpanel3).to_be_visible()

    # Click hide-menu to hide the static menu
    hidemenu = controller.InputActionButton(page, "hide_menu")
    hidemenu.click()

    # Expect the Menu to be hidden
    navpanel3 = controller.NavPanel(page, "tabs", "s1").loc
    expect(navpanel3).to_be_hidden()

    # Click show-menu to show the static menu again
    showmenu = controller.InputActionButton(page, "show_menu")
    showmenu.click()

    # Expect the Menu to be visible again
    expect(page.get_by_role("button", name="Menu", exact=True)).to_be_visible()

    # Click the Menu button to show the static menu and expect the panels to be visible again
    page.get_by_role("button", name="Menu", exact=True).click()
    navpanel3 = controller.NavPanel(page, "tabs", "s1").loc
    expect(navpanel3).to_be_visible()
