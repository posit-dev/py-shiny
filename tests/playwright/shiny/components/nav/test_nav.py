from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page

from shiny.playwright.controls import (
    LayoutNavSetBar,
    LayoutNavSetCardPill,
    LayoutNavSetCardTab,
    LayoutNavSetCardUnderline,
    LayoutNavSetPill,
    LayoutNavSetPillList,
    LayoutNavSetTab,
    LayoutNavSetUnderline,
)
from shiny.run import ShinyAppProc


def test_nav(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Update the page size to be wider
    page.set_viewport_size({"width": 1500, "height": 800})

    @dataclass
    class LayoutInfo:
        control: type[
            LayoutNavSetBar
            | LayoutNavSetCardPill
            | LayoutNavSetCardTab
            | LayoutNavSetCardUnderline
            | LayoutNavSetPill
            | LayoutNavSetPillList
            | LayoutNavSetTab
            | LayoutNavSetUnderline
        ]
        verify: str

    nav_data: list[LayoutInfo] = [
        LayoutInfo(LayoutNavSetTab, "navset_tab()"),
        LayoutInfo(LayoutNavSetPill, "navset_pill()"),
        LayoutInfo(LayoutNavSetUnderline, "navset_underline()"),
        LayoutInfo(LayoutNavSetCardTab, "navset_card_tab()"),
        LayoutInfo(LayoutNavSetCardPill, "navset_card_pill()"),
        LayoutInfo(LayoutNavSetCardUnderline, "navset_card_underline()"),
        LayoutInfo(LayoutNavSetPillList, "navset_pill_list()"),
        LayoutInfo(LayoutNavSetBar, "page_navbar()"),
    ]

    for nav_info in nav_data:
        el_name = nav_info.verify.replace("()", "")
        element = nav_info.control(page, el_name)
        element.expect_nav_values(["a", "b", "c"])
        element.expect_value("a")
        element.expect_content(nav_info.verify + ": tab a content")
        element.set("b")
        element.expect_value("b")
        element.expect_content(nav_info.verify + ": tab b content")
