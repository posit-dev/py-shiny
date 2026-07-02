from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

CONTAINER = ".card-body:has(#auto_scroll_stream)"

# Read-only check (never mutates scrollTop): true once the container has been
# at the bottom with a stable scroll position for 3 consecutive polls.
# 20px tolerance: shinychat scrolls to the exact bottom, so this only absorbs
# subpixel rounding; shinychat's own re-pin tolerance is 50px.
AT_BOTTOM_STABLE_SCRIPT = """(selector) => {
    const el = document.querySelector(selector);
    if (!el) return false;

    const atBottom = (el.scrollTop + el.clientHeight) >= (el.scrollHeight - 20);
    const changed =
        el.__abLastTop !== el.scrollTop || el.__abLastHeight !== el.scrollHeight;
    el.__abLastTop = el.scrollTop;
    el.__abLastHeight = el.scrollHeight;

    if (!atBottom || changed) {
        el.__abStableCount = 0;
        return false;
    }
    el.__abStableCount = (el.__abStableCount || 0) + 1;
    return el.__abStableCount >= 2;
}"""

# True once scrollHeight has grown past minHeight and been stable for 3
# consecutive polls (i.e. the new chunk has fully rendered and settled).
GROWN_AND_SETTLED_SCRIPT = """(args) => {
    const el = document.querySelector(args.selector);
    if (!el) return false;

    if (el.scrollHeight <= args.minHeight || el.__ghLastHeight !== el.scrollHeight) {
        el.__ghLastHeight = el.scrollHeight;
        el.__ghStableCount = 0;
        return false;
    }
    el.__ghStableCount = (el.__ghStableCount || 0) + 1;
    return el.__ghStableCount >= 2;
}"""


def scroll_state(page: Page) -> dict[str, float]:
    return page.evaluate(
        """(sel) => {
            const el = document.querySelector(sel);
            return {
                scrollTop: el.scrollTop,
                scrollHeight: el.scrollHeight,
                clientHeight: el.clientHeight,
            };
        }""",
        CONTAINER,
    )


def expect_at_bottom(page: Page, *, timeout: float = 30_000) -> None:
    try:
        page.wait_for_function(
            AT_BOTTOM_STABLE_SCRIPT,
            arg=CONTAINER,
            polling=250,
            timeout=timeout,
        )
    except Exception as e:
        raise RuntimeError(
            f"Container never settled at bottom: {scroll_state(page)}"
        ) from e


def next_chunk_and_wait_for_render(
    page: Page, button: controller.InputActionButton, i: int
) -> None:
    height_before = scroll_state(page)["scrollHeight"]
    button.click()
    stream = page.locator("#auto_scroll_stream")
    expect(stream).to_contain_text(f"CHUNK-{i}-END", timeout=30_000)
    page.wait_for_function(
        GROWN_AND_SETTLED_SCRIPT,
        arg={"selector": CONTAINER, "minHeight": height_before},
        polling=250,
        timeout=30_000,
    )


def test_auto_scroll_pinning(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    next_chunk = controller.InputActionButton(page, "next_chunk")
    stream = page.locator("#auto_scroll_stream")
    # The empty stream element has zero height, so wait for attachment (not
    # visibility) before sending the first chunk.
    expect(stream).to_be_attached(timeout=30_000)

    # Chunk 1 creates the overflow; shinychat binds to the scrollable parent on
    # a 200ms throttle, so pinning assertions start once content overflows.
    next_chunk_and_wait_for_render(page, next_chunk, 1)

    # Phase A: while pinned, the container follows each appended chunk.
    for i in (2, 3):
        next_chunk_and_wait_for_render(page, next_chunk, i)
        expect_at_bottom(page)

    # Phase B: scrolling away from the bottom unpins; new content must NOT
    # drag the container back down.
    page.evaluate(f"""() => document.querySelector({CONTAINER!r}).scrollTo(0, 0)""")
    page.wait_for_function(
        f"""() => document.querySelector({CONTAINER!r}).scrollTop === 0"""
    )
    next_chunk_and_wait_for_render(page, next_chunk, 4)
    state = scroll_state(page)
    assert state["scrollTop"] < 50, f"Unpinned container was scrolled: {state}"

    # Phase C: scrolling back to the bottom re-pins; the next chunk is
    # followed again.
    page.evaluate(f"""() => {{
            const el = document.querySelector({CONTAINER!r});
            el.scrollTo(0, el.scrollHeight);
        }}""")
    expect_at_bottom(page)
    next_chunk_and_wait_for_render(page, next_chunk, 5)
    expect_at_bottom(page)
