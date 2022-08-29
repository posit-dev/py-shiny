# pyright: reportUnknownMemberType=false

import re
from playwright.sync_api import Page, expect
from conftest import ShinyAppProc


def test_airmass(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
