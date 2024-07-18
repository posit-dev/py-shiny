from __future__ import annotations

from colors import bg_color, fg_color
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.playwright.expect._internal import expect_class_to_have_value
from shiny.run import ShinyAppProc


def test_colors_are_rgb() -> None:
    assert bg_color.startswith("rgb(")
    assert fg_color.startswith("rgb(")


def test_sidebar_bg_colors(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    for i in range(3, 5):
        content = page.locator(f"#m{i}")
        sidebar = page.locator(f"#s{i}")

        main_layout = sidebar.locator("..")

        open_desktop = "always" if i <= 2 else "open"
        open_mobile = "always" if i <= 2 else "closed"
        position_val = "left" if i % 2 == 1 else "right"

        expect(main_layout).to_have_attribute("data-open-desktop", open_desktop)
        expect(main_layout).to_have_attribute("data-open-mobile", open_mobile)

        expect_class_to_have_value(
            main_layout,
            "sidebar-right",
            has_class=position_val == "right",
        )

        expect(content).to_have_text(f"Main content - {i}")
        expect(sidebar).to_have_text(f"Sidebar content - {i}")

        # Only works if css file is loaded
        expect(sidebar).to_have_css("background-color", bg_color)
        expect(sidebar).to_have_css("color", fg_color)

    s3 = controller.Sidebar(page, "s3")
    s3.expect_position("left")
    s4 = controller.Sidebar(page, "s4")
    s4.expect_position("right")
