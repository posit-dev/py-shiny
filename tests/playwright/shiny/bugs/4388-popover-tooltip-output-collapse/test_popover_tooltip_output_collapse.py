"""
Regression test for bslib #1326 / shiny #4388.

A dynamically-rendered output (`@render.ui`) inside a title-less popover or
tooltip used to collapse to 0 width, so its `ResizeObserver` never fired and
the output stayed stuck "recalculating" forever. Vendored bslib CSS gives
`.shiny-html-output` a non-zero `min-width` inside `.popover`/`.tooltip`
containers so the observer always sees a size change and the output
correctly reports itself as visible.

This test checks both that the output renders its content, and that the
`min-width` CSS rule the fix relies on is actually shipped and applied.
"""

from playwright.sync_api import Locator, Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def expect_output_rendered(page: Page, loc_output: Locator) -> None:
    expect(loc_output).to_have_text("Dynamic content")
    expect(loc_output).to_be_visible()

    min_width = loc_output.evaluate("(el) => window.getComputedStyle(el).minWidth")
    assert min_width != "0px", (
        "`.shiny-html-output` inside a popover/tooltip should have a "
        "non-zero min-width (bslib #1326 / shiny #4388 workaround), "
        f"but computed min-width was {min_width!r}"
    )


def test_popover_output_does_not_collapse(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    popover = controller.Popover(page, "popover_id")
    popover.expect_active(False)
    popover.set(True)
    popover.expect_active(True)

    loc_output = popover.get_loc_overlay_body().locator(".shiny-html-output")
    expect_output_rendered(page, loc_output)


def test_tooltip_output_does_not_collapse(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    tooltip = controller.Tooltip(page, "tooltip_id")
    tooltip.expect_active(False)
    tooltip.set(True)
    tooltip.expect_active(True)

    loc_output = tooltip.get_loc_overlay_body().locator(".shiny-html-output")
    expect_output_rendered(page, loc_output)
