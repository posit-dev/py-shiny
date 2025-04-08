from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_sidebar_bookmarking_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test sidebar bookmarking
    left_sidebar = controller.Sidebar(page, "sidebar_left")
    right_sidebar = controller.Sidebar(page, "first-sidebar_right")

    left_sidebar.expect_open(True)
    right_sidebar.expect_open(True)

    left_sidebar.set(False)
    right_sidebar.set(False)

    left_sidebar.expect_open(False)
    right_sidebar.expect_open(False)

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    left_sidebar.set(True)
    right_sidebar.set(True)

    # reload page
    page.reload()

    left_sidebar.expect_open(False)
    right_sidebar.expect_open(False)
