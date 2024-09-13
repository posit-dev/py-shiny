from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_tooltip_test_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    tooltip_auto = controller.Tooltip(page, "default_tooltip_auto")
    tooltip_auto.expect_active(False)
    tooltip_auto.set(True)
    tooltip_auto.expect_active(True)
    tooltip_auto.expect_body("An auto message")
    tooltip_auto.expect_placement(
        "right"
    )  # since there is no space on the top, it defaults to right

    tooltip_top = controller.Tooltip(page, "default_tooltip_top")
    tooltip_top.expect_active(False)
    tooltip_top.set(True)
    tooltip_top.expect_active(True)
    tooltip_top.expect_body("A top message")
    tooltip_top.expect_placement("top")

    tooltip_right = controller.Tooltip(page, "default_tooltip_right")
    tooltip_right.expect_active(False)
    tooltip_right.set(True)
    tooltip_right.expect_active(True)
    tooltip_right.expect_body("A right message")
    tooltip_right.expect_placement("right")

    tooltip_left = controller.Tooltip(page, "default_tooltip_left")
    tooltip_left.expect_active(False)
    tooltip_left.set(True)
    tooltip_left.expect_active(True)
    tooltip_left.expect_body("A left message")
    tooltip_left.expect_placement("left")
