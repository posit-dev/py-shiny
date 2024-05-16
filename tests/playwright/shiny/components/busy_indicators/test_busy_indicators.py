import os
from urllib.parse import urlparse

from conftest import ShinyAppProc
from controls import InputRadioButtons, InputTaskButton, expect_not_to_have_class
from playwright.sync_api import Page, expect


def get_spinner_computed_property(
    page: Page, element_id: str, property_name: str
) -> str:
    expect(page.locator(element_id)).to_be_visible()
    return page.evaluate(
        f"window.getComputedStyle(document.querySelector('{element_id}'), '::after').getPropertyValue('{property_name}');"
    )


def get_pulse_computed_property(page: Page, property_name: str) -> str:
    expect(page.locator("html body")).to_be_visible()
    return page.evaluate(
        f"window.getComputedStyle(document.documentElement, '::after').getPropertyValue('{property_name}');"
    )


def test_busy_indicators(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    spinner_type = InputRadioButtons(page, "busy_indicator_type")
    render_button = InputTaskButton(page, "rerender")

    # verify spinner indicator behavior
    # plot spinner
    height = get_spinner_computed_property(page, "#pulse-plot", "height")
    assert height == "50px"
    background_color = get_spinner_computed_property(
        page, "#pulse-plot", "background-color"
    )
    assert background_color == "rgb(128, 128, 0)"
    mask_image_url = get_spinner_computed_property(page, "#pulse-plot", "mask-image")
    svg_name = os.path.basename(urlparse(mask_image_url).path).rstrip('")')
    assert svg_name == "pulse.svg"
    width = get_spinner_computed_property(page, "#pulse-plot", "width")
    assert width == "50px"

    # ring spinner
    height = get_spinner_computed_property(page, "#ring-plot", "height")
    assert height == "10px"
    background_color = get_spinner_computed_property(
        page, "#ring-plot", "background-color"
    )
    assert background_color == "rgb(255, 0, 0)"
    mask_image_url = get_spinner_computed_property(page, "#ring-plot", "mask-image")
    svg_name = os.path.basename(urlparse(mask_image_url).path).rstrip('")')
    assert svg_name == "ring.svg"
    width = get_spinner_computed_property(page, "#ring-plot", "width")
    assert width == "10px"

    # verify pulse indicator behavior
    # timeout is set to 8000ms to avoid the 5000ms default timeout
    expect_not_to_have_class(page.locator("html"), "shiny-busy", timeout=8000)
    spinner_type.set("pulse")
    render_button.click()
    height = get_pulse_computed_property(page, "height")
    assert height == "100px"
    background_image = get_pulse_computed_property(page, "background-image")
    assert background_image == "linear-gradient(45deg, rgb(0, 0, 255), rgb(255, 0, 0))"
