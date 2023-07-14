from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import Card
from playwright.sync_api import Page

app = x_create_doc_example_fixture("card")


def test_card(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    card = Card(page, "card1")
    card.expect_header_to_contain_text("This is the header")
    card.expect_footer_to_contain_text("This is the footer")
    card.expect_body_to_contain_text("This is the title\nThis is the body.", 0)
    card.expect_body_to_contain_text("This is still the body.", 2)
    card.expect_body_title_to_contain_text("This is the title", 0)
    card.expect_full_screen(False)
    card.open_full_screen()
    card.expect_full_screen(True)
    card.close_full_screen()
    card.expect_full_screen(False)

