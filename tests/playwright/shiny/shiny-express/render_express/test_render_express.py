from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("render_express")

EXPECT_TIMEOUT = 30 * 1000


def test_render_express(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    expect(page.get_by_text("Name")).to_have_count(1, timeout=EXPECT_TIMEOUT)
    expect(page.get_by_text("Socrates")).to_have_count(1, timeout=EXPECT_TIMEOUT)
