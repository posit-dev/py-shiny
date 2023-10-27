from __future__ import annotations

from colors import bg_color, fg_color
from conftest import ShinyAppProc
from controls import Sidebar
from playwright.sync_api import Page, expect


def test_colors_are_rgb() -> None:
    assert bg_color.startswith("rgb(")
    assert fg_color.startswith("rgb(")


def test_sidebar_bg_colors(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    first_content = page.locator("#m1")
    first_sidebar = page.locator("#s1")

    main_layout = first_sidebar.locator("..")

    expect(main_layout).to_have_attribute("data-bslib-sidebar-open", "always")

    expect(first_content).to_have_text("Main content - 1")
    expect(first_sidebar).to_have_text("Sidebar content - 1")

    # Only works if css file is loaded
    expect(first_sidebar).to_have_css("background-color", bg_color)
    expect(first_sidebar).to_have_css("color", fg_color)

    s1 = Sidebar(page, "s1")
    s1.expect_position("left")
    s2 = Sidebar(page, "s2")
    s2.expect_position("right")
