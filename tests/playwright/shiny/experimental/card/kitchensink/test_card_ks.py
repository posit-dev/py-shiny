from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def get_body_tag_name(card: controller.Card) -> str:
    body_tag_name = (
        card.loc_body.locator("*").nth(0).evaluate("el => el.tagName.toLowerCase()")
    )
    return body_tag_name


"""
For each card we want to test
Max Height and Min Height: The tests assert the max-height and min-height CSS properties applied to the card.
Header and Footer: The tests verify the presence and content of the header and footer elements within each card.
Body Element: The tests assert the tag name used for the body element within each card (e.g., <span>, <p>, <h1>, <h3>, <h5>).
Fullscreen Availability and State: The tests check whether the fullscreen feature is available for a particular card and verify its initial state (fullscreen or not). For cards with fullscreen support, the tests open and close the fullscreen mode and assert the expected behavior.
"""


def test_card_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    card = controller.Card(page, "card1")
    card.expect_max_height(None)
    card.expect_min_height(None)
    card.expect_height(None)
    card.expect_header("Check for header")
    card.expect_footer("Check for footer")
    card.expect_body(
        [
            "\nThis is the body of a card with default height w/ fullscreen",
        ]
    )
    card.expect_full_screen(False)
    card.set_full_screen(True)
    card.expect_full_screen(True)
    card.set_full_screen(False)
    card.expect_full_screen(False)

    card = controller.Card(page, "card2")
    card.expect_max_height(None)
    card.expect_min_height(None)
    card.expect_height(None)
    card.expect_header(None)
    card.expect_footer(None)
    card.expect_body(
        ["\nThis is the body without a header of a footer - No Fullscreen\n"]
    )
    assert get_body_tag_name(card) == "p"
    card.expect_full_screen(False)
    card.expect_full_screen_available(False)

    card = controller.Card(page, "card3")
    card.expect_max_height("500px")
    card.expect_min_height("200px")
    card.expect_header("Fill is False. Fullscreen is False")
    card.expect_footer(None)
    card.expect_body(["Max height and min height are set."])
    assert get_body_tag_name(card) == "h3"
    card.expect_full_screen_available(False)
