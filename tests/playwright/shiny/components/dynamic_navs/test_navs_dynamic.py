# import pytest
import pytest
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Page begins with 2 tabs: "Hello" and "Foo" and a nav menu with 2 static items.
    navset_tab = controller.NavsetTab(page, "tabs")

    # Click add-foo to add a new Foo tab
    addfoo = controller.InputActionButton(page, "addFoo")
    addfoo.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Foo", "Foo-1", "Static 1", "Static 2"]
    )

    # Click hide-tab to hide the Foo tabs
    hidetab = controller.InputActionButton(page, "hideTab")
    hidetab.click()

    # Expect the Foo tabs to be hidden
    expect(
        page.get_by_role("presentation").filter(has_text="This is the Foo tab")
    ).to_be_hidden()
    expect(page.get_by_role("presentation").filter(has_text="Foo-")).to_be_hidden()

    # Click show-tab to show the Foo tabs again
    showtab = controller.InputActionButton(page, "showTab")
    showtab.click()

    # Expect the Foo tabs to be visible again
    expect(
        page.get_by_role("presentation").filter(has_text="This is the Foo tab")
    ).not_to_be_hidden()
    expect(page.get_by_role("presentation").filter(has_text="Foo-")).not_to_be_hidden()

    # Click remove-foo to remove the Foo tabs
    removefoo = controller.InputActionButton(page, "removeFoo")
    removefoo.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Static 1", "Static 2"]
    )

    # Click add to add a dynamic tab
    add = controller.InputActionButton(page, "add")
    add.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Static 1", "Dynamic-1", "Static 2"]
    )

    # Click add again to add another dynamic tab
    add.click()
    controller.NavsetTab(page, "tabs").expect_nav_titles(
        ["Hello", "Static 1", "Dynamic-1", "Dynamic-2", "Static 2"]
    )

    # Click hide-menu to hide the static menu
    hidemenu = controller.InputActionButton(page, "hideMenu")
    hidemenu.click()

    # Expect the Menu to be hidden
    expect(page.get_by_role("presentation").filter(has_text="Static")).to_be_hidden()

    # Click show-menu to show the static menu again
    showmenu = controller.InputActionButton(page, "showMenu")
    showmenu.click()

    # Expect the Menu to be visible again
    expect(
        page.get_by_role("presentation").filter(has_text="Static")
    ).not_to_be_hidden()
