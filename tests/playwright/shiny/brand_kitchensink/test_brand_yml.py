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
        "primary_value_box": {
            "background-color": "rgb(111, 66, 193)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "secondary_value_box": {
            "background-color": "rgb(64, 64, 64)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "info_value_box": {
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
        "default_btn": {
            "background-color": "rgba(0, 0, 0, 0)",
            "color": "rgb(64, 64, 64)",
            "font-family": re.compile(r"Monda.*"),
        },
        "primary_btn": {
            "background-color": "rgb(111, 66, 193)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "secondary_btn": {
            "background-color": "rgb(64, 64, 64)",
            "color": "rgb(248, 248, 248)",
            "font-family": re.compile(r"Monda.*"),
        },
        "success_btn": {
            "background-color": "rgb(40, 167, 69)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "danger_btn": {
            "background-color": "rgb(255, 127, 80)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "warning_btn": {
            "background-color": "rgb(255, 215, 0)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
        "info_btn": {
            "background-color": "rgb(23, 162, 184)",
            "color": "rgb(26, 26, 26)",
            "font-family": re.compile(r"Monda.*"),
        },
    }

    component_mapping = {
        "primary_value_box": controller.ValueBox,
        "secondary_value_box": controller.ValueBox,
        "info_value_box": controller.ValueBox,
        "switch1": controller.InputSwitch,
        "out_text1": controller.OutputText,
        "default_btn": controller.InputActionButton,
        "primary_btn": controller.InputActionButton,
        "secondary_btn": controller.InputActionButton,
        "success_btn": controller.InputActionButton,
        "danger_btn": controller.InputActionButton,
        "warning_btn": controller.InputActionButton,
        "info_btn": controller.InputActionButton,
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
