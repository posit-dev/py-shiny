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

    nav_data = {
        "navset_tab": {
            "control": LayoutNavsetTab,
            "verify": "navset_tab()"
        },
        "navset_pill": {
            "control": LayoutNavSetPill,
            "verify": "navset_pill()"
        },
        "navset_underline": {
            "control": LayoutNavSetUnderline,
            "verify": "navset_underline()"
        },
        "navset_card_tab": {
            "control": LayoutNavSetCardTab,
            "verify": "navset_card_tab()"
        },
        "navset_card_pill": {
            "control": LayoutNavSetCardPill,
            "verify": "navset_card_pill()"
        },
        "navset_card_underline": {
            "control": LayoutNavSetCardUnderline,
            "verify": "navset_card_underline()"
        },
        "navset_pill_list": {
            "control": LayoutNavSetPillList,
            "verify": "navset_pill_list()"
        },
        "page_navbar": {
            "control": LayoutNavSetBar,
            "verify": "page_navbar"
        }
    }

    def tester(tab_name):
        tab = nav_data[tab_name]['control'](page, tab_name)
        tab.expect_nav_values(["a", "b", "c"])
        tab.expect_value("a")
        tab.expect_content(nav_data[tab_name]['verify'] + ": tab a content")
        tab.set("b")
        tab.expect_value("b")
        tab.expect_content(nav_data[tab_name]['verify'] + ": tab b content")

    nav_list = [
        "navset_tab", "navset_pill", "navset_underline", "navset_card_tab",
        "navset_card_pill", "navset_card_underline", "navset_pill_list", "page_navbar"
    ]
    failures = []
    # soft assert
    for nav in nav_list:
        try:
            tester(nav)
        except Exception as e:
            failures.append({"element": nav, "error": e})
    assert failures == []

