from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page

from shiny.playwright.controller import (
    NavsetBar,
    NavsetCardPill,
    NavsetCardTab,
    NavsetCardUnderline,
    NavsetPill,
    NavsetPillList,
    NavsetTab,
    NavsetUnderline,
)
from shiny.run import ShinyAppProc


def test_nav(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Update the page size to be wider
    page.set_viewport_size({"width": 1500, "height": 800})

    @dataclass
    class LayoutInfo:
        control: type[
            NavsetBar
            | NavsetCardPill
            | NavsetCardTab
            | NavsetCardUnderline
            | NavsetPill
            | NavsetPillList
            | NavsetTab
            | NavsetUnderline
        ]
        verify: str

    nav_data: list[LayoutInfo] = [
        LayoutInfo(NavsetTab, "navset_tab()"),
        LayoutInfo(NavsetPill, "navset_pill()"),
        LayoutInfo(NavsetUnderline, "navset_underline()"),
        LayoutInfo(NavsetCardTab, "navset_card_tab()"),
        LayoutInfo(NavsetCardPill, "navset_card_pill()"),
        LayoutInfo(NavsetCardUnderline, "navset_card_underline()"),
        LayoutInfo(NavsetPillList, "navset_pill_list()"),
        LayoutInfo(NavsetBar, "page_navbar()"),
    ]

    for nav_info in nav_data:
        el_name = nav_info.verify.replace("()", "")
        element = nav_info.control(page, el_name)
        element.expect_nav_values(["a", "b", "c"])
        element.expect_value("a")
        element._expect_content_text(nav_info.verify + ": tab a content")
        element.set("b")
        element.expect_value("b")
        element._expect_content_text(nav_info.verify + ": tab b content")
