"""
Regression test for #2597: `controller.NavPanel.click()` expands a navbar that
has collapsed behind its toggler before clicking the tab.
"""

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_click_tab_in_collapsed_navbar(page: Page, local_app: ShinyAppProc) -> None:
    # Narrower than the navbar's `md` breakpoint (768px), so the tabs collapse.
    page.set_viewport_size({"width": 500, "height": 800})
    page.goto(local_app.url)

    selected = controller.OutputText(page, "selected")
    selected.expect_value("Selected: A")

    controller.NavPanel(page, "navbar", "B").click()
    controller.NavPanel(page, "navbar", "B").expect_active(True)
    selected.expect_value("Selected: B")

    # A tab inside a dropdown menu, in a navbar that is collapsed again.
    page.reload()
    selected.expect_value("Selected: A")
    controller.NavPanel(page, "navbar", "C").click()
    controller.NavPanel(page, "navbar", "C").expect_active(True)
    selected.expect_value("Selected: C")
