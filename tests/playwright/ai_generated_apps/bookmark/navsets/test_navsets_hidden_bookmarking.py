from typing import Callable

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture("app-hidden.py")


@pytest.mark.parametrize(
    "navset_name,navset_variant,navset_controller",
    [
        ("navset_hidden", "default", controller.NavsetHidden),
    ],
)
def test_navset_hidden_bookmarking(
    page: Page,
    app: ShinyAppProc,
    navset_name: str,
    navset_variant: str,
    navset_controller: Callable[[Page, str], controller._navs._NavsetBase],
) -> None:
    page.goto(app.url)

    # Non-module navsets
    navset_collection = controller.NavsetTab(page, "navsets_collection")
    navset_collection.set(navset_name)
    navset_id = f"{navset_name}_{navset_variant}"
    navset_cont = navset_controller(page, navset_id)
    navset_btn = controller.InputActionButton(page, f"{navset_id}_button")
    navset_btn.click()
    navset_btn.click()

    # Module navsets
    mod_navset_collection = controller.NavsetTab(page, "first-navsets_collection")
    mod_navset_collection.set(navset_name)
    mod_navset_cont = navset_controller(page, f"first-{navset_id}")
    mod_navset_btn = controller.InputActionButton(page, f"first-{navset_id}_button")
    mod_navset_btn.click()

    # Selecting a panel in a hidden navset requires a server round trip (button
    # click -> reactive effect -> `ui.update_navset()` -> client applies the
    # selection and reports it back to the server). Wait for the selections to
    # reach the DOM before bookmarking; otherwise the bookmark can serialize
    # stale navset values.
    navset_cont.expect_value(f"{navset_id}_c")
    mod_navset_cont.expect_value(f"{navset_id}_b")

    existing_url = page.url

    # Click bookmark button
    controller.InputBookmarkButton(page).click()
    page.wait_for_url(lambda url: url != existing_url, timeout=5 * 1000)

    # Reload page
    page.reload()

    # Assert
    navset_collection.expect_value(navset_name)
    navset_cont.expect_value(f"{navset_id}_c")
    mod_navset_collection.expect_value(navset_name)
    mod_navset_cont.expect_value(f"{navset_id}_b")
