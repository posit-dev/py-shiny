from __future__ import annotations

from colors import bg_color, fg_color
from conftest import ShinyAppProc
from controls import Sidebar, _expect_class_value
from playwright.sync_api import Page, expect


def test_colors_are_rgb() -> None:
    assert bg_color.startswith("rgb(")
    assert fg_color.startswith("rgb(")


def test_sidebar_bg_colors(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    for i in range(1, 5):
        content = page.locator(f"#m{i}")
        sidebar = page.locator(f"#s{i}")

        main_layout = sidebar.locator("..")

        open_val = "always" if i <= 2 else "desktop"
        position_val = "left" if i % 2 == 1 else "right"

        expect(main_layout).to_have_attribute("data-bslib-sidebar-open", open_val)

        _expect_class_value(main_layout, "sidebar-right", position_val == "right")

        expect(content).to_have_text(f"Main content - {i}")
        expect(sidebar).to_have_text(f"Sidebar content - {i}")

        # Only works if css file is loaded
        expect(sidebar).to_have_css("background-color", bg_color)
        expect(sidebar).to_have_css("color", fg_color)

    s1 = Sidebar(page, "s1")
    s1.expect_position("left")
    s2 = Sidebar(page, "s2")
    s2.expect_position("right")
