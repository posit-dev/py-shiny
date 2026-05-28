"""
Regression test for https://github.com/posit-dev/py-shiny/issues/2263

When a @render.ui output finishes recalculating while its containing tab is
hidden, the recalculating overlay (CSS class) must clear when the tab becomes
visible again. Prior to the fix, IntersectionObserver could not detect
visibility changes on shiny-html-output elements because they use
display:contents (which removes their box model).
"""

import re

from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc


def test_recalculating_clears_on_hidden_tab(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    # Wait for the tab UI to load
    page.wait_for_selector('[role="tab"]', timeout=10000)

    # Switch to Tab B before the 1.5s async delay completes, so that
    # Tab A's @render.ui recalculates while hidden
    page.get_by_role("tab", name="Tab B").click()

    # Wait for collections to load (the async delay is 1.5s)
    tab_b_select = page.locator("#b-internal_selected_collection")
    expect(tab_b_select).to_be_visible(timeout=10000)

    # Tab B's output should not be stuck in recalculating
    tab_b_output = page.locator("#b-collection_selector")
    expect(tab_b_output).not_to_have_class(re.compile("recalculating"), timeout=5000)

    # Switch back to Tab A — this is where the bug manifested
    page.get_by_role("tab", name="Tab A").click()

    # Tab A's select should become visible
    tab_a_select = page.locator("#a-internal_selected_collection")
    expect(tab_a_select).to_be_visible(timeout=5000)

    # The output container must NOT be stuck in recalculating
    tab_a_output = page.locator("#a-collection_selector")
    expect(tab_a_output).not_to_have_class(re.compile("recalculating"), timeout=5000)

    # The text output should show the selected value
    expect(page.locator("#a_selected")).to_have_text("Selected: col_1", timeout=5000)
