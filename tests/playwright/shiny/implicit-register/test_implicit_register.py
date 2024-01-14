from conftest import ShinyAppProc
from playwright.sync_api import Page, expect


def test_implicit_register(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    expect(page.locator("#out2")).to_have_text("One")
    expect(page.locator("#out3")).to_have_text("Two")
    expect(page.locator("#out4")).to_have_text("Two")
    expect(page.locator("#out1")).to_be_empty()
