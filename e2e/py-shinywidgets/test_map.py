from conftest import ShinyAppProc
from playwright.sync_api import Page, Locator, expect

from controls import SliderInput, LeafletContainer, TextOutput

def test_ipywidgets(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Verify map loads on initial app load
    leaflet_container = LeafletContainer(page, "map")
    leaflet_container.expect.to_be_visible()
    leaflet_container.locate_map_output().is_visible()

    # Adjust Map zoom level with slider and check map reloads
    slider_input = SliderInput(page, "zoom")
    map_style_1 = leaflet_container.loc.locator(".leaflet-proxy").get_attribute("style")
    slider_input.move_slider(0)
    map_style_2 = leaflet_container.loc.locator(".leaflet-proxy").get_attribute("style")

    assert map_style_1 != map_style_2

    # Adjust Map zoom level from map and check slider updates
    leaflet_container.map_zoom_in().click()
    assert slider_input.get_slider_value() == "2"

    leaflet_container.map_zoom_out().click()
    assert slider_input.get_slider_value() == "1"

    # TODO: low priority
    # Double click on the map that would adjust the zoom level and slide updates
    # mouse = leaflet_container.loc.page.mouse
    # mouse.dblclick(8, 10)

    # Change slider and see if latitude, longitude shown in the text output
    slider_input.move_slider(0.4)
    txt_ob = TextOutput(page, "map_bounds")
    # TODO: Find a better way to see if the output text has expected latitude, longitude
    assert txt_ob.contains_digit(txt_ob.get_text())

