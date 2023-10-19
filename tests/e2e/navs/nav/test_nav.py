from conftest import ShinyAppProc
from controls import (
    LayoutNavSetBar,
    LayoutNavSetCardPill,
    LayoutNavSetCardTab,
    LayoutNavSetPill,
    LayoutNavSetPillList,
    LayoutNavsetTab,
)
from playwright.sync_api import Page


def test_nav(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # make it in a funcn and then loop through it
    # navset_tab
    navset = LayoutNavsetTab(page, "navset_tab")
    navset.expect_nav_values(["a", "b", "c"])
    navset.expect_value("a")
    navset.expect_content("navset_tab(): tab a content")
    navset.set("b")
    navset.expect_value("b")
    navset.expect_content("navset_tab(): tab b content")

    # # navset_pill
    navset_pill = LayoutNavSetPill(page, "navset_pill")
    navset_pill.expect_nav_values(["a", "b", "c"])
    navset_pill.expect_value("a")
    navset_pill.expect_content("navset_pill(): tab a content")
    navset_pill.set("b")
    navset_pill.expect_value("b")
    navset_pill.expect_content("navset_pill(): tab b content")

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

    # navset_pill_list
    navset_card_pill = LayoutNavSetPillList(page, "navset_pill_list")
    navset_card_pill.expect_nav_values(["a", "b", "c"])
    navset_card_pill.expect_value("a")
    navset_card_pill.expect_content("navset_pill_list(): tab a content")
    navset_card_pill.set("b")
    navset_card_pill.expect_value("b")
    navset_card_pill.expect_content("navset_pill_list(): tab b content")

    # Page_navbar
    navset_bar = LayoutNavSetBar(page, "navbar_id")
    navset_bar.expect_nav_values(["a", "b", "c"])
    navset_bar.expect_value("a")
    navset_bar.expect_content("page_navbar: tab a content")
    navset_bar.set("b")
    navset_bar.expect_value("b")
    navset_bar.expect_content("page_navbar: tab b content")
