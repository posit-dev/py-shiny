from __future__ import annotations

from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputActionButton, InputDarkMode, LayoutNavSetBar
from playwright.sync_api import Page

app = create_doc_example_core_fixture("input_dark_mode")


def test_input_dark_mode_follows_system_setting(page: Page, app: ShinyAppProc) -> None:
    page.emulate_media(color_scheme="light")
    page.goto(app.url)

    mode_switch = InputDarkMode(page, "mode")
    mode_switch.expect_mode("light")
    mode_switch.expect_wc_attribute("data-bs-theme")

    page.emulate_media(color_scheme="dark")
    mode_switch = InputDarkMode(page, "mode")
    mode_switch.expect_mode("dark")
    mode_switch.expect_wc_attribute("data-bs-theme")


def test_input_dark_mode_switch(page: Page, app: ShinyAppProc) -> None:
    page.emulate_media(color_scheme="light")
    page.goto(app.url)

    mode_switch = InputDarkMode(page, "mode")
    navbar = LayoutNavSetBar(page, "page")
    make_light = InputActionButton(page, "make_light")
    make_dark = InputActionButton(page, "make_dark")

    # Test clicking the dark mode switch
    mode_switch.expect_mode("light").click().expect_mode("dark")

    # Change to nav panel two and trigger server-side changes
    navbar.set("Two")

    make_light.click()
    mode_switch.expect_mode("light")

    make_dark.click()
    mode_switch.expect_mode("dark")
