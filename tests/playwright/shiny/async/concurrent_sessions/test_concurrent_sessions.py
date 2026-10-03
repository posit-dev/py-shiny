from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_slow_async_effect_does_not_block_other_tab(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)
    other = page.context.new_page()
    try:
        other.goto(local_app.url)
        ticks = controller.OutputText(other, "ticks")
        ticks.expect.not_to_have_text("")

        # Start a 3s async effect in the first tab, then check the second tab's
        # timer keeps ticking while it runs.
        controller.InputActionButton(page, "block").click()
        page.wait_for_timeout(300)
        before = int(ticks.loc.inner_text())
        other.wait_for_timeout(1000)
        after = int(ticks.loc.inner_text())

        assert after - before >= 3, f"other tab stalled: {before} -> {after}"
    finally:
        other.close()
