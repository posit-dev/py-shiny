from conftest import ShinyAppProc
from playwright.sync_api import Page, expect

from controls import SliderInput


def test_ipywidgets(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Verify map loads on initial app load
    map = page.locator("#map")
    expect(map).to_have_class("shiny-ipywidget-output shiny-bound-output")
    expect(map).to_be_visible()

    # TODO: Adjust Map zoom level and check map reloads
    # Note: The slider in this app is a bit different than others

