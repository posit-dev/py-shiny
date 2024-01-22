from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("render_express")

EXPECT_TIMEOUT = 30 * 1000


def test_render_express(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    expect(page.get_by_text("Text outside of render express call")).to_have_count(
        1, timeout=EXPECT_TIMEOUT
    )
    expect(page.get_by_text("Text inside of render express call")).to_have_count(
        1, timeout=EXPECT_TIMEOUT
    )
    expect(page.get_by_text("Dynamic slider value: 50")).to_have_count(
        1, timeout=EXPECT_TIMEOUT
    )
