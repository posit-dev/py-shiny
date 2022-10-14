import re

from conftest import ShinyAppProc
from playwright.sync_api import Page, expect

def test_file_upload(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
