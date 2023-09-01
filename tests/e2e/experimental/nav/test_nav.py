# import pytest
from conftest import ShinyAppProc
from controls import (
    NavSetBar,
    NavSetCardPill,
    NavSetCardTab,
    NavSetPill,
    NavSetPillList,
    NavsetTab,
)
from playwright.sync_api import Page


# @pytest.mark.parametrize("nav_type", ["navbar_id", "navset_tab", "navset_pill", "navset_card_tab", "navset_card_pill", "navset_pill_list"])
def test_nav(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # navset_tab
    navset = NavsetTab(page, "navset_tab")
    navset.expect_nav_items(["a", "b", "c"])
    navset.set("b")
    navset.expect_value("b")
    navset.expect_nav_content("b", "navset_tab(): tab b content")

    # navset_pill
    navset_pill = NavSetPill(page, "navset_pill")
    navset_pill.expect_nav_items(["a", "b", "c"])
    navset_pill.set("b")
    navset_pill.expect_value("b")
    navset_pill.expect_nav_content("b", "navset_pill(): tab b content")

    # navset_card_tab
    navset_card_tab = NavSetCardTab(page, "navset_card_tab")
    navset_card_tab.expect_nav_items(["a", "b", "c"])
    navset_card_tab.set("b")
    navset_card_tab.expect_value("b")
    navset_card_tab.expect_nav_content("b", "navset_card_tab(): tab b content")

    # navset_card_pill
    navset_card_pill = NavSetCardPill(page, "navset_card_pill")
    navset_card_pill.expect_nav_items(["a", "b", "c"])
    navset_card_pill.set("b")
    navset_card_pill.expect_value("b")
    navset_card_pill.expect_nav_content("b", "navset_card_pill(): tab b content")

    # navset_pill_list
    navset_card_pill = NavSetPillList(page, "navset_pill_list")
    navset_card_pill.expect_nav_items(["a", "b", "c"])
    navset_card_pill.set("b")
    navset_card_pill.expect_value("b")
    navset_card_pill.expect_nav_content("b", "navset_pill_list(): tab b content")

    # Page_navbar
    # not working - check if locator structure is not same
    # navset_bar = NavSetBar(page, "navbar_id")
    # page_navbar.expect_nav_items(["a", "b", "c"])
    # navset_bar.set("b")
    # navset_bar.expect_value("b")
    # navset_bar.expect_nav_content("b", "page_navbar: tab b content")
