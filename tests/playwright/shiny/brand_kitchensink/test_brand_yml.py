import re
from typing import Any, Callable, Dict

from conftest import create_example_fixture
from playwright.sync_api import Locator, Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_example_fixture("brand")


def test_brand_yml_kitchensink(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expected_styles = {
        "value_box_primary": {
            "background-color": "rgb(111, 66, 193)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "value_box_secondary": {
            "background-color": "rgb(64, 64, 64)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "value_box_info": {
            "background-color": "rgb(23, 162, 184)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "switch1": {
            "background-color": "rgba(0, 0, 0, 0)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "out_text1": {
            "background-color": "rgb(26, 26, 26)",
            "color": "rgb(40, 167, 69)",
            "font-family": re.compile(r"Share Tech Mono.*"),
        },
        "btn_default": {
            "background-color": "rgba(0, 0, 0, 0)",
            "color": "rgb(64, 64, 64)",
            "font-family": re.compile(r"Monda.*"),
        },
        "btn_primary": {
            "background-color": "rgb(111, 66, 193)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "btn_secondary": {
            "background-color": "rgb(64, 64, 64)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "btn_success": {
            "background-color": "rgb(40, 167, 69)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "btn_danger": {
            "background-color": "rgb(255, 127, 80)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "btn_warning": {
            "background-color": "rgb(255, 215, 0)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "btn_info": {
            "background-color": "rgb(23, 162, 184)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
    }

    component_mapping = {
        "value_box_primary": controller.ValueBox,
        "value_box_secondary": controller.ValueBox,
        "value_box_info": controller.ValueBox,
        "switch1": controller.InputSwitch,
        "out_text1": controller.OutputText,
        "btn_default": controller.InputActionButton,
        "btn_primary": controller.InputActionButton,
        "btn_secondary": controller.InputActionButton,
        "btn_success": controller.InputActionButton,
        "btn_danger": controller.InputActionButton,
        "btn_warning": controller.InputActionButton,
        "btn_info": controller.InputActionButton,
    }

    locator_mapping: Dict[type[Any], Callable[[Any], Locator]] = {
        controller.ValueBox: lambda component: component.loc_container,
        controller.InputSwitch: lambda component: component.loc_label,
        controller.OutputText: lambda component: component.loc,
        controller.InputActionButton: lambda component: component.loc,
    }

    # Iterate over expected styles and perform assertions
    for component_name, styles in expected_styles.items():
        component_class = component_mapping[component_name]
        component = component_class(page, component_name)
        locator = locator_mapping[component_class](component)
        for property_name, expected_value in styles.items():
            expect(locator).to_have_css(property_name, expected_value)

    # inline-code block
    expect(page.get_by_text("@reactive.effect")).to_have_css(
        "background-color", "rgba(26, 26, 26, 0.867)"
    )
    expect(page.get_by_text("@reactive.effect")).to_have_css(
        "color", "rgb(255, 215, 0)"
    )
    expect(page.get_by_text("@reactive.effect")).to_have_css(
        "font-family", re.compile(r"Share Tech Mono.*")
    )
