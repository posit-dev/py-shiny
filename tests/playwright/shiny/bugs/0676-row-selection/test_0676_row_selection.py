from __future__ import annotations

from conftest import ShinyAppProc
from playwright.sync_api import Page, expect


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # The purpose of this test is to make sure that the data grid can work on Pandas
    # data frames that use an index that is not simply 0-based integers.

    row1 = page.locator("#grid tbody tr:nth-child(1)")
    row3 = page.locator("#grid tbody tr:nth-child(3)")
    result_loc = page.locator("#detail tbody tr:nth-child(1) td:nth-child(1)")
    debug_loc = page.locator("#debug")

    expect(row3).to_be_visible()
    expect(row3.locator("td:nth-child(1)")).to_have_text("three")
    expect(debug_loc).to_have_text("()")

    expect(result_loc).not_to_be_attached()
    row3.click()
    expect(result_loc).to_have_text("three")
    expect(debug_loc).to_have_text("(2,)")

    # Ensure that keys are in sorted order, not the order in which they were selected
    row1.click()
    expect(debug_loc).to_have_text("(0, 2)")
