import re

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_navset_bar_options(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    page_navbar = controller.PageNavbar(page, "page_navbar")
    expect(page_navbar._loc_navbar).to_have_class(re.compile(r"(^|\s)bg-primary(\s|$)"))
    expect(page_navbar._loc_navbar).to_have_attribute("data-bs-theme", "dark")

    inner_navbar = controller.NavsetBar(page, "inner_navset_bar")
    expect(inner_navbar._loc_navbar).to_have_class(re.compile(r"(^|\s)bg-light(\s|$)"))
    expect(inner_navbar._loc_navbar).to_have_attribute("data-bs-theme", "light")
