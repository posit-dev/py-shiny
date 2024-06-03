from shiny.test import Page, ShinyAppProc
from shiny.test._controls import Card


def test_card(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    card = Card(page, "card1")
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
    card.expect_full_screen_open(False)
    card.open_full_screen()
    card.expect_full_screen_open(True)
    card.close_full_screen()
    card.expect_full_screen_open(False)
