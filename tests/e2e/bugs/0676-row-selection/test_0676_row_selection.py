from __future__ import annotations

from conftest import ShinyAppProc
from playwright.sync_api import Page, expect


def test_row_selection(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # The purpose of this test is to make sure that the data grid can work on Pandas
    # data frames that use an index that is not simply 0-based integers.

    row3 = page.locator("#grid tbody tr:nth-child(3)")
    result_loc = page.locator("#detail tbody tr:nth-child(1) td:nth-child(1)")

    expect(row3).to_be_visible()
    expect(row3.locator("td:nth-child(1)")).to_have_text("three")

    expect(result_loc).not_to_be_attached()
    row3.click()
    expect(result_loc).to_have_text("three")
