from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

SCROLLED_TO_BOTTOM_SCRIPT = """(selector) => {
    const element = document.querySelector(selector);
    if (!element) return false;

    // Get the exact scroll values
    const scrollTop = element.scrollTop;
    const scrollHeight = element.scrollHeight;
    const clientHeight = element.clientHeight;

    // Check if the element is scrollable
    if (scrollHeight <= clientHeight) return false;

    // Check if we're at the bottom. Match shinychat's own bottomTolerance
    // (10px), with extra headroom for browser subpixel rounding and
    // end-of-stream layout shifts.
    return (scrollTop + clientHeight) >= (scrollHeight - 15);
}"""

# shinychat auto-scrolls via scrollTo({behavior: "smooth"}), so after the last
# stream chunk arrives the scroll animation may still be running. Poll until
# scrollTop is stable across two consecutive reads before asserting position.
SCROLL_SETTLED_SCRIPT = """(selector) => {
    const el = document.querySelector(selector);
    if (!el) return false;
    const now = el.scrollTop;
    if (el.__lastScrollTop === now) return true;
    el.__lastScrollTop = now;
    return false;
}"""


def expect_element_scrolled_to_bottom(
    page: Page,
    selector: str,
    *,
    timeout: float = 30_000,
) -> None:
    page.wait_for_function(
        SCROLL_SETTLED_SCRIPT,
        arg=selector,
        polling=250,
        timeout=10_000,
    )
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
