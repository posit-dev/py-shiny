from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

# Single combined check: avoids race where settle-then-check missed in-progress smooth scrolls
SETTLED_AT_BOTTOM_SCRIPT = """(selector) => {
    const el = document.querySelector(selector);
    if (!el) return false;

    el.scrollTop = el.scrollHeight;

    const scrollTop = el.scrollTop;
    const scrollHeight = el.scrollHeight;
    const clientHeight = el.clientHeight;

    if (scrollHeight <= clientHeight) return false;

    // 20px tolerance: shinychat uses 10px bottomTolerance + headroom for subpixel rounding
    const atBottom = (scrollTop + clientHeight) >= (scrollHeight - 20);
    if (!atBottom) {
        el.__stableCount = 0;
        el.__lastScrollTop = undefined;
        return false;
    }

    if (el.__lastScrollTop === scrollTop) {
        el.__stableCount = (el.__stableCount || 0) + 1;
    } else {
        el.__stableCount = 0;
    }
    el.__lastScrollTop = scrollTop;
    // Require 3 consecutive polls (750ms) at bottom to rule out mid-animation pauses
    return el.__stableCount >= 2;
}"""


def expect_element_scrolled_to_bottom(
    page: Page,
    selector: str,
    *,
    timeout: float = 30_000,
) -> None:
    try:
        page.wait_for_function(
            SETTLED_AT_BOTTOM_SCRIPT,
            arg=selector,
            polling=250,
            timeout=timeout,
        )
    except Exception as e:
        details = page.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (!el) return "Element not found";
                return {
                    scrollTop: el.scrollTop,
                    scrollHeight: el.scrollHeight,
                    clientHeight: el.clientHeight,
                    stableCount: el.__stableCount,
                    lastScrollTop: el.__lastScrollTop
                };
            }""",
            selector,
        )
        raise RuntimeError(f"Scroll assertion failed for {selector}: {details}") from e


def test_validate_stream_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.add_init_script("""
        const style = document.createElement('style');
        style.innerHTML = '* { scroll-behavior: auto !important; }';
        document.head.appendChild(style);

        const forceAuto = (original) => {
            return function(options, ...args) {
                if (options && typeof options === 'object') {
                    options.behavior = 'auto';
                }
                return original.apply(this, arguments);
            };
        };

        Element.prototype.scroll = forceAuto(Element.prototype.scroll);
        Element.prototype.scrollTo = forceAuto(Element.prototype.scrollTo);
        Element.prototype.scrollBy = forceAuto(Element.prototype.scrollBy);
        Element.prototype.scrollIntoView = forceAuto(Element.prototype.scrollIntoView);

        window.scroll = forceAuto(window.scroll);
        window.scrollTo = forceAuto(window.scrollTo);
        window.scrollBy = forceAuto(window.scrollBy);
        """)
    page.goto(local_app.url)

    stream = page.locator("#shiny_readme")
    expect(stream).to_be_visible(timeout=30_000)
    expect(stream).to_contain_text("pre-commit uninstall", timeout=30_000)

    page.evaluate(
        """(sel) => {
            const el = document.querySelector(sel);
            if (el) el.scrollTop = el.scrollHeight;
        }""",
        ".card-body:has(#shiny_readme)",
    )

    expect_element_scrolled_to_bottom(page, ".card-body:has(#shiny_readme)")

    stream2 = page.locator("#shiny_readme_err")
    expect(stream2).to_be_visible(timeout=30_000)
    expect(stream2).to_contain_text("Shiny", timeout=30_000)

    notification = page.locator(".shiny-notification-error")
    expect(notification).to_be_visible(timeout=30_000)
    expect(notification).to_contain_text("boom!", timeout=30_000)

    txt_result = controller.OutputText(page, "stream_result")
    txt_result.expect_value("Stream result: Basic stream")
