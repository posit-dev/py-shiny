import re
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Callable, Dict

import pytest
from conftest import create_example_fixture
from packaging.version import Version
from playwright.sync_api import Locator, Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

# brand_yml <= 0.1.1 returns a bare `Tag` from `BrandLogoResource.tagify()`.
# htmltools 0.7.0 (posit-dev/py-htmltools#105) tightened the Tagifiable
# contract to require a fully-tagified return, so rendering a brand logo
# with old brand_yml + new htmltools raises `TypeError` at the render
# boundary. Drop this module-level skip — and bump py-shiny's `brand_yml`
# floor — once brand_yml 0.1.2 (posit-dev/brand-yml#115) ships to PyPI.
try:
    _brand_yml_version = Version(version("brand_yml"))
except PackageNotFoundError:
    _brand_yml_version = None  # pyright: ignore[reportAssignmentType]
_brand_yml_min = Version("0.1.2")
pytestmark = pytest.mark.skipif(
    _brand_yml_version is None or _brand_yml_version < _brand_yml_min,
    reason=(
        f"brand_yml {_brand_yml_version} predates the htmltools 0.7.0"
        f" Tagifiable fix; requires brand_yml >= {_brand_yml_min}"
        " (posit-dev/brand-yml#115)."
    ),
)

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
