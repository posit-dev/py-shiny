import pytest
from conftest import ShinyAppProc
from controls import (
    LayoutNavSetBar,
    LayoutNavSetCardPill,
    LayoutNavSetCardTab,
    LayoutNavSetCardUnderline,
    LayoutNavSetPill,
    LayoutNavSetPillList,
    LayoutNavsetTab,
    LayoutNavSetUnderline,
)
from playwright.sync_api import Page


@pytest.mark.skip_browser("webkit")
def test_nav(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Update the page size to be wider
    page.set_viewport_size({"width": 1500, "height": 800})

    # make it in a funcn and then loop through it
    # navset_tab
    navset_tab = LayoutNavsetTab(page, "navset_tab")
    navset_tab.expect_nav_values(["a", "b", "c"])
    navset_tab.expect_value("a")
    navset_tab.expect_content("navset_tab(): tab a content")
    navset_tab.set("b")
    navset_tab.expect_value("b")
    navset_tab.expect_content("navset_tab(): tab b content")

    # # navset_pill
    navset_pill = LayoutNavSetPill(page, "navset_pill")
    navset_pill.expect_nav_values(["a", "b", "c"])
    navset_pill.expect_value("a")
    navset_pill.expect_content("navset_pill(): tab a content")
    navset_pill.set("b")
    navset_pill.expect_value("b")
    navset_pill.expect_content("navset_pill(): tab b content")

    # navset_underline
    navset_underline = LayoutNavSetUnderline(page, "navset_underline")
    navset_underline.expect_nav_values(["a", "b", "c"])
    navset_underline.expect_value("a")
    navset_underline.expect_content("navset_underline(): tab a content")
    navset_underline.set("b")
    navset_underline.expect_value("b")
    navset_underline.expect_content("navset_underline(): tab b content")

    # navset_card_tab
    navset_card_tab = LayoutNavSetCardTab(page, "navset_card_tab")
    navset_card_tab.expect_nav_values(["a", "b", "c"])
    navset_card_tab.expect_value("a")
    navset_card_tab.expect_content("navset_card_tab(): tab a content")
    navset_card_tab.set("b")
    navset_card_tab.expect_value("b")
    navset_card_tab.expect_content("navset_card_tab(): tab b content")

    # navset_card_pill
    navset_card_pill = LayoutNavSetCardPill(page, "navset_card_pill")
    navset_card_pill.expect_nav_values(["a", "b", "c"])
    navset_card_pill.expect_value("a")
    navset_card_pill.expect_content("navset_card_pill(): tab a content")
    navset_card_pill.set("b")
    navset_card_pill.expect_value("b")
    navset_card_pill.expect_content("navset_card_pill(): tab b content")

    # navset_card_underline
    navset_card_underline = LayoutNavSetCardUnderline(page, "navset_card_underline")
    navset_card_underline.expect_nav_values(["a", "b", "c"])
    navset_card_underline.expect_value("a")
    navset_card_underline.expect_content("navset_card_underline(): tab a content")
    navset_card_underline.set("b")
    navset_card_underline.expect_value("b")
    navset_card_underline.expect_content("navset_card_underline(): tab b content")

    # navset_pill_list
    navset_card_pill = LayoutNavSetPillList(page, "navset_pill_list")
    navset_card_pill.expect_nav_values(["a", "b", "c"])
    navset_card_pill.expect_value("a")
    navset_card_pill.expect_content("navset_pill_list(): tab a content")
    navset_card_pill.set("b")
    navset_card_pill.expect_value("b")
    navset_card_pill.expect_content("navset_pill_list(): tab b content")

    # Page_navbar
    navset_bar = LayoutNavSetBar(page, "page_navbar")
    navset_bar.expect_nav_values(["a", "b", "c"])
    navset_bar.expect_value("a")
    navset_bar.expect_content("page_navbar: tab a content")
    navset_bar.set("b")
    navset_bar.expect_value("b")
    navset_bar.expect_content("page_navbar: tab b content")
