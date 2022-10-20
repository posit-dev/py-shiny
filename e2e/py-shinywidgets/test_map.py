from conftest import ShinyAppProc
from playwright.sync_api import Page, expect

from controls import SliderInput


def test_ipywidgets(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    map = page.locator("#map")
    expect(map).to_be_visible()
    expect(map).to_have_class("shiny-ipywidget-output shiny-bound-output")


    #Adjust Map zoom level with slider and check map reloads
    map_style_1=page.locator(".leaflet-container .leaflet-proxy").get_attribute("style")
    print("Map style is.." + str(map_style_1))

    SliderInput(page, "zoom").move_slider(0)

    map_style_2=page.locator(".leaflet-container .leaflet-proxy").get_attribute("style")
    print("Map style is.." + str(map_style_2))

    assert map_style_1 != map_style_2

    # TODO: Adjust Map zoom level from map and check slider updates
    # a. Using + and - sign

    # b. Double click on the map that would adjust the zoom level and slide updates
    # TODO: Check dragging of the map and see if latitude, longitude updates

