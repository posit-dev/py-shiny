# pyright: reportUnknownMemberType=false

import re
from conftest import ShinyAppProc
from controls import SliderInput

from playwright.sync_api import Page, expect

def test_spiro_app(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    SliderInput(page, "start").move_slider(1)
    SliderInput(page, "step").move_slider(0.5)

    SliderInput(page, "origin").move_slider_range(0.2, 0.08)

    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
