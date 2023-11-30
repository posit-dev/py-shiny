from conftest import ShinyAppProc
from controls import Card, OutputTextVerbatim
from playwright.sync_api import Page


def test_express_page_fillable(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    card = Card(page, "card")
    bounding_box = card.loc.bounding_box()
    if bounding_box is not None:
        assert bounding_box["height"] > 300
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
