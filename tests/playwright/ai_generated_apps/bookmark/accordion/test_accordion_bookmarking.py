from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_accordion_bookmarking_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test accordion bookmarking
    acc_single = controller.Accordion(page, "acc_single")
    acc_single.expect_open(["Section A"])
    acc_single.set(["Section B"])

    acc_mod = controller.Accordion(page, "first-acc_mod")
    acc_mod.expect_open(["Section A"])
    acc_mod.set(["Section C"])

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    # reload page
    page.reload()

    acc_single.expect_open(["Section B"])
    acc_mod.expect_open(["Section C"])

    acc_single.set([])
    acc_mod.set([])

    bookmark_button.click()

    # reload page
    page.reload()

    acc_single.expect_open([])
    acc_mod.expect_open([])
