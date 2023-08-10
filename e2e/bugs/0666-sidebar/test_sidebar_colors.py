from __future__ import annotations

from colors import bg_color, fg_color
from conftest import ShinyAppProc
from playwright.sync_api import Page, expect


def test_colors_are_rgb() -> None:
    assert bg_color.startswith("rgb(")
    assert fg_color.startswith("rgb(")


def test_sidebar_bg_colors(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    main_content = page.locator("#main-content")
    main_sidebar = page.locator("#main-sidebar")
    main_layout = main_sidebar.locator("..")

    # x_content = page.locator("#x-content")
    # x_sidebar = page.locator("#x-sidebar")
    # x_layout = x_sidebar.locator("..")

    expect(main_layout).to_have_attribute("data-bslib-sidebar-open", "always")
    # expect(x_layout).to_have_attribute("data-bslib-sidebar-open", "always")

    expect(main_content).to_have_text("`main` - Main content")
    # expect(x_content).to_have_text("`x` - Main content")
    expect(main_sidebar).to_have_text("`main` - Sidebar content")
    # expect(x_sidebar).to_have_text("`x` - Sidebar content")

    # Only works if css file is loaded
    expect(main_sidebar).to_have_css("background-color", bg_color)
    # expect(x_sidebar).to_have_css("background-color", bg_color)
    expect(main_sidebar).to_have_css("color", fg_color)
    # expect(x_sidebar).to_have_css("color", fg_color)
