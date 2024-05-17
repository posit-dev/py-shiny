import os
from urllib.parse import urlparse

from conftest import ShinyAppProc
from controls import InputRadioButtons, InputTaskButton, OutputTextVerbatim
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

    # Verify spinner indicator behavior
    spinner_properties = [
        ("#pulse-plot", "50px", "rgb(128, 128, 0)", "pulse.svg"),
        ("#ring-plot", "10px", "rgb(255, 0, 0)", "ring.svg"),
        ("#bars-plot", "20px", "rgb(0, 128, 0)", "bars.svg"),
        ("#dots-plot", "30px", "rgb(0, 0, 255)", "dots.svg"),
    ]

    for element_id, height, background_color, svg_name in spinner_properties:
        assert get_spinner_computed_property(page, element_id, "height") == height
        assert (
            get_spinner_computed_property(page, element_id, "background-color")
            == background_color
        )
        mask_image_url = get_spinner_computed_property(page, element_id, "mask-image")
        assert os.path.basename(urlparse(mask_image_url).path).rstrip('")') == svg_name
        assert get_spinner_computed_property(page, element_id, "width") == height

    # Verify pulse indicator behavior
    output_txt = OutputTextVerbatim(page, "counter")
    output_txt.expect_value("0")
    spinner_type.set("pulse")
    render_button.click()
    # since we are not using locators wait for up to 2 secs
    for _ in range(200):
        if get_pulse_computed_property(page, "height") != "auto":
            break
        page.wait_for_timeout(10)
    assert get_pulse_computed_property(page, "height") == "100px"
    assert (
        get_pulse_computed_property(page, "background-image")
        == "linear-gradient(45deg, rgb(0, 0, 255), rgb(255, 0, 0))"
    )
    output_txt.expect_value("1")
    # since output value is 1, nothing is computing
    # verify the pulse indicator is removed
    assert get_pulse_computed_property(page, "height") == "auto"
