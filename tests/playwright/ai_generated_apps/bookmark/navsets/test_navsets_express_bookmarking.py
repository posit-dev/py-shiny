from typing import Type

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture("app-express.py")


@pytest.mark.parametrize(
    "navset_name,navset_variant,navset_controller",
    [
        ("navset_bar", "default", controller.NavsetBar),
        ("navset_pill", "default", controller.NavsetPill),
        ("navset_underline", "default", controller.NavsetUnderline),
        ("navset_tab", "default", controller.NavsetTab),
        ("navset_pill_list", "default", controller.NavsetPillList),
        ("navset_card_pill", "default", controller.NavsetCardPill),
        ("navset_card_tab", "default", controller.NavsetCardTab),
        ("navset_card_underline", "default", controller.NavsetCardUnderline),
    ],
)
def test_navsets_bookmarking_demo(
    page: Page,
    app: ShinyAppProc,
    navset_name: str,
    navset_variant: str,
    navset_controller: Type[controller._navs._NavsetBase],
) -> None:
    page.goto(app.url)

    # Non-module navsets
    navset_collection = controller.NavsetTab(page, "navsets_collection")
    navset_collection.set(navset_name)
    navset_cont = navset_controller(page, f"{navset_name}_{navset_variant}")
    navset_cont.set(f"{navset_name}_c")

    # Module navsets
    mod_navset_collection = controller.NavsetTab(page, "first-navsets_collection")
    mod_navset_collection.set(navset_name)
    mod_navset_cont = navset_controller(page, f"first-{navset_name}_{navset_variant}")
    mod_navset_cont.set(f"{navset_name}_b")

    # Click bookmark button
    controller.InputBookmarkButton(page).click()

    # Reload page
    page.reload()

    # Assert
    navset_collection.expect_value(navset_name)
    navset_cont.expect_value(f"{navset_name}_c")
    mod_navset_collection.expect_value(navset_name)
    mod_navset_cont.expect_value(f"{navset_name}_b")
