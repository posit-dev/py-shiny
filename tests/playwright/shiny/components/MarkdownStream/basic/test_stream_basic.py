from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

SCROLLED_TO_BOTTOM_SCRIPT = """(selector) => {
    const element = document.querySelector(selector);
    if (!element) return false;

    const scrollTop = element.scrollTop;
    const scrollHeight = element.scrollHeight;
    const clientHeight = element.clientHeight;

    if (scrollHeight <= clientHeight) return false;

    return Math.abs((scrollTop + clientHeight) - scrollHeight) <= 3;
}"""


def expect_element_scrolled_to_bottom(
    page: Page,
    selector: str,
    *,
    timeout: float = 30_000,
) -> None:
    page.wait_for_function(
        SCROLLED_TO_BOTTOM_SCRIPT,
        arg=selector,
        timeout=timeout,
    )


def test_validate_stream_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    stream = page.locator("#shiny_readme")
    expect(stream).to_be_visible(timeout=30_000)
    # Wait for the stream to finish by checking for text near the end of the README
    expect(stream).to_contain_text("pre-commit uninstall", timeout=30_000)

    # Check that the card body container (the parent of the markdown stream) is scrolled
    # all the way to the bottom
    expect_element_scrolled_to_bottom(page, ".card-body:has(#shiny_readme)")

    stream2 = page.locator("#shiny_readme_err")
    expect(stream2).to_be_visible(timeout=30_000)
    expect(stream2).to_contain_text("Shiny", timeout=30_000)

    notification = page.locator(".shiny-notification-error")
    expect(notification).to_be_visible(timeout=30_000)
    expect(notification).to_contain_text("boom!", timeout=30_000)

    txt_result = controller.OutputText(page, "stream_result")
    txt_result.expect_value("Stream result: Basic stream")
