from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc


def test_inclusion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    expect(page.locator("body > p").first).to_have_text("Heyo!")
    expect(page.locator("body > p").last).to_have_text("Also here!")
