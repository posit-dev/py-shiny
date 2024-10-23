from typing import Union

import pytest
from examples.example_apps import reruns, reruns_delay
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_navbar(page: Page, local_app: ShinyAppProc) -> None:
    values = ["a", "b", "c"]

    def verify_panel_updates(
        elem: Union[
            controller.PageNavbar,
            controller.NavsetCardTab,
            controller.NavsetCardPill,
            controller.NavsetBar,
        ]
    ) -> None:
        a_panel = elem.nav_panel("a")
        b_panel = elem.nav_panel("b")
        c_panel = elem.nav_panel("c")

        a_panel.click()
        a_panel.expect_active(True)
        b_panel.expect_active(False)
        c_panel.expect_active(False)
        assert (
            f"{elem.id}(): tab a content\n"
            in elem.get_loc_active_content().all_text_contents()
        )

        b_panel.click()
        a_panel.expect_active(False)
        b_panel.expect_active(True)
        c_panel.expect_active(False)
        assert (
            f"{elem.id}(): tab b content\n"
            in elem.get_loc_active_content().all_text_contents()
        )

        c_panel.click()
        a_panel.expect_active(False)
        b_panel.expect_active(False)
        c_panel.expect_active(True)
        assert (
            f"{elem.id}(): tab c content\n"
            in elem.get_loc_active_content().all_text_contents()
        )

    page.goto(local_app.url)

    nav_bar = controller.PageNavbar(page, "page_navbar")
    nav_bar.expect_nav_values(values)
    verify_panel_updates(nav_bar)

    navset_card_tab = controller.NavsetCardTab(page, "navset_card_tab")
    navset_card_tab.expect_nav_values(values)
    verify_panel_updates(navset_card_tab)

    navset_card_pill = controller.NavsetCardPill(page, "navset_card_pill")
    navset_card_pill.expect_nav_values(values)
    verify_panel_updates(navset_card_pill)

    navset_bar = controller.NavsetBar(page, "navset_bar")
    navset_bar.expect_nav_values(values)
    verify_panel_updates(navset_bar)
