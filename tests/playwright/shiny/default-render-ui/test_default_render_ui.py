from shiny.test import Page, ShinyAppProc, expect


def test_implicit_register(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    expect(page.locator("#txt")).to_have_text("Hello")
