import re

from playwright.sync_api import Page, expect

from shiny.playwright.controller import InputRadioButtons
from shiny.run import ShinyAppProc


def test_bookmark_modules(page: Page, local_app: ShinyAppProc):

    page.goto(local_app.url)

    letter = InputRadioButtons(page, "letter")
    letter.expect_selected("A")
    letter.set("C")

    expect(page.locator("div.modal-body > textarea")).to_have_value(
        re.compile(r"letter=%22C%22")
    )

    assert "?" not in page.url
