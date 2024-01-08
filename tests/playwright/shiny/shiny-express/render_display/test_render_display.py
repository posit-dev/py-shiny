from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("render_display")

EXPECT_TIMEOUT = 30 * 1000


def test_render_display(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)
    expect(page.get_by_text("Text outside of render display call")).to_have_count(
        1, timeout=EXPECT_TIMEOUT
    )
    expect(page.get_by_text("Text inside of render display call")).to_have_count(
        1, timeout=EXPECT_TIMEOUT
    )
    expect(page.get_by_text("Dynamic slider value: 50")).to_have_count(
        1, timeout=EXPECT_TIMEOUT
    )
