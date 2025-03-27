from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_navsets_bookmarking_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Non-module navsets
    navset_collection = controller.NavsetTab(page, "navsets_collection")
    navset_collection.set("navset_underline")
    navset_underline = controller.NavsetUnderline(page, "navset_underline_default")
    navset_underline.set("navset_underline_c")
    navset_collection.set("navset_card_underline")
    navset_card_underline = controller.NavsetCardUnderline(
        page, "navset_card_underline_default"
    )
    navset_card_underline.set("navset_card_underline_c")

    # module navsets
    mod_navset_collection = controller.NavsetTab(page, "first-navsets_collection")
    mod_navset_collection.set("navset_underline")
    mod_navset_underline = controller.NavsetUnderline(
        page, "first-navset_underline_default"
    )
    mod_navset_underline.set("navset_underline_c")
    mod_navset_collection.set("navset_card_underline")
    mod_navset_card_underline = controller.NavsetCardUnderline(
        page, "first-navset_card_underline_default"
    )
    mod_navset_card_underline.set("navset_card_underline_c")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    # reload page
    page.reload()

    navset_card_underline.expect_value("navset_card_underline_c")
    navset_collection.expect_value("navset_card_underline")
    mod_navset_card_underline.expect_value("navset_card_underline_c")
    mod_navset_collection.expect_value("navset_card_underline")
