from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_card(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    card = controller.Card(page, "card1")
    card.expect_max_height(None)
    card.expect_min_height(None)
    card.expect_height(None)
    card.expect_header("This is the header")
    card.expect_footer("This is the footer")
    card.expect_body(
        [
            "\nThis is the title\nThis is the body.\n",
            "\n\n",
            "\nThis is still the body.\n",
        ]
    )
    card.expect_full_screen(False)
    card.set_full_screen(True)
    card.expect_full_screen(True)
    card.set_full_screen(False)
    card.expect_full_screen(False)
