from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


async def is_element_scrolled_to_bottom(page: Page, selector: str) -> bool:
    return await page.evaluate(
        """(selector) => {
        const element = document.querySelector(selector);
        if (!element) return false;

        // Get the exact scroll values (rounded to handle float values)
        const scrollTop = Math.round(element.scrollTop);
        const scrollHeight = Math.round(element.scrollHeight);
        const clientHeight = Math.round(element.clientHeight);

        // Check if we're at the bottom (allowing for 1px difference due to rounding)
        return Math.abs((scrollTop + clientHeight) - scrollHeight) <= 1;
    }""",
        selector,
    )


@skip_on_webkit
async def test_validate_stream_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    stream = controller.MarkdownStream(page, "shiny-readme")

    expect(stream.loc).to_be_visible(timeout=30 * 1000)
    stream.expect_content("pip install shiny")

    # Check that the card body container (the parent of the markdown stream) is scrolled
    # all the way to the bottom
    is_scrolled = await is_element_scrolled_to_bottom(page, ".card-body")
    assert is_scrolled, "The card body container should be scrolled to the bottom"
