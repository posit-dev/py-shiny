from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

# Scroll/auto-scroll behavior is covered by the deterministic test in
# ../auto_scroll/; this test focuses on streaming a large document at full
# speed, error propagation, and the stream result API.


def test_validate_stream_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    stream = page.locator("#shiny_readme")
    expect(stream).to_be_visible(timeout=30_000)
    expect(stream).to_contain_text("pre-commit uninstall", timeout=30_000)

    stream2 = page.locator("#shiny_readme_err")
    expect(stream2).to_be_visible(timeout=30_000)
    expect(stream2).to_contain_text("Shiny", timeout=30_000)

    notification = page.locator(".shiny-notification-error")
    expect(notification).to_be_visible(timeout=30_000)
    expect(notification).to_contain_text("boom!", timeout=30_000)

    txt_result = controller.OutputText(page, "stream_result")
    txt_result.expect_value("Stream result: Basic stream")
