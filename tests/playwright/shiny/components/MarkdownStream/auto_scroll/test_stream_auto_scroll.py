from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

PINNED = ".card-body:has(#auto_scroll_stream)"
UNPINNED = ".card-body:has(#no_auto_scroll_stream)"

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


# Scrolls the container and flags when the resulting scroll *event* is
# delivered. shinychat updates its pinned/unpinned state inside its own scroll
# handler, and scroll events are dispatched asynchronously (on Firefox, tied to
# paint ticks that can lag under CI load) — so waiting on scrollTop alone races
# the event delivery. Our once-listener registers after shinychat's, so by the
# time the flag is set, shinychat has already processed the same event.
SCROLL_TO_SCRIPT = """(args) => {
    const el = document.querySelector(args.selector);
    delete el.__testScrollEventSeen;
    el.addEventListener(
        "scroll",
        () => { el.__testScrollEventSeen = true; },
        { once: true },
    );
    el.scrollTo(0, args.to === "bottom" ? el.scrollHeight : 0);
}"""


def scroll_to_and_wait_for_scroll_event(page: Page, selector: str, to: str) -> None:
    page.evaluate(SCROLL_TO_SCRIPT, {"selector": selector, "to": to})
    page.wait_for_function(
        """(sel) => document.querySelector(sel).__testScrollEventSeen === true""",
        arg=selector,
        timeout=30_000,
    )


def scroll_state(page: Page, selector: str) -> dict[str, float]:
    return page.evaluate(
        """(sel) => {
            const el = document.querySelector(sel);
            return {
                scrollTop: el.scrollTop,
                scrollHeight: el.scrollHeight,
                clientHeight: el.clientHeight,
            };
        }""",
        selector,
    )


def expect_at_bottom(page: Page, selector: str, *, timeout: float = 30_000) -> None:
    try:
        page.wait_for_function(
            AT_BOTTOM_STABLE_SCRIPT,
            arg=selector,
            polling=250,
            timeout=timeout,
        )
    except Exception as e:
        raise RuntimeError(
            f"{selector} never settled at bottom: {scroll_state(page, selector)}"
        ) from e


def expect_not_scrolled(page: Page, selector: str) -> None:
    state = scroll_state(page, selector)
    assert state["scrollTop"] < 50, f"{selector} was scrolled: {state}"


def next_chunk_and_wait_for_render(
    page: Page, button: controller.InputActionButton, i: int
) -> None:
    heights = {
        sel: scroll_state(page, sel)["scrollHeight"] for sel in (PINNED, UNPINNED)
    }
    button.click()
    for stream_id in ("auto_scroll_stream", "no_auto_scroll_stream"):
        expect(page.locator(f"#{stream_id}")).to_contain_text(
            f"CHUNK-{i}-END", timeout=30_000
        )
    for sel, height_before in heights.items():
        page.wait_for_function(
            GROWN_AND_SETTLED_SCRIPT,
            arg={"selector": sel, "minHeight": height_before},
            polling=250,
            timeout=30_000,
        )


def test_auto_scroll_pinning(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    next_chunk = controller.InputActionButton(page, "next_chunk")
    # The empty stream elements have zero height, so wait for attachment (not
    # visibility) before sending the first chunk.
    expect(page.locator("#auto_scroll_stream")).to_be_attached(timeout=30_000)
    expect(page.locator("#no_auto_scroll_stream")).to_be_attached(timeout=30_000)

    # Chunk 1 creates the overflow; shinychat binds to the scrollable parent on
    # a 200ms throttle, so pinning assertions start once content overflows.
    next_chunk_and_wait_for_render(page, next_chunk, 1)

    # Phase A: the auto-scroll container follows each appended chunk, while the
    # auto_scroll=False container (negative control) must never move. This also
    # proves the at-bottom assertion is not vacuous: the same chunks fail it
    # when auto-scroll is off.
    for i in (2, 3):
        next_chunk_and_wait_for_render(page, next_chunk, i)
        expect_at_bottom(page, PINNED)
        expect_not_scrolled(page, UNPINNED)

    # Phase B: scrolling away from the bottom unpins; new content must NOT
    # drag the container back down. Waiting for the scroll event (not just
    # scrollTop) guarantees shinychat has registered the unpin before the next
    # chunk arrives.
    scroll_to_and_wait_for_scroll_event(page, PINNED, "top")
    next_chunk_and_wait_for_render(page, next_chunk, 4)
    expect_not_scrolled(page, PINNED)

    # Phase C: scrolling back to the bottom re-pins; the next chunk is
    # followed again. Same rationale: shinychat only re-pins inside its scroll
    # handler, so wait for the event to be delivered before streaming more.
    scroll_to_and_wait_for_scroll_event(page, PINNED, "bottom")
    expect_at_bottom(page, PINNED)
    next_chunk_and_wait_for_render(page, next_chunk, 5)
    expect_at_bottom(page, PINNED)
    expect_not_scrolled(page, UNPINNED)
