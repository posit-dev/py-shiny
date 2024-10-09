from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_popover_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    popover_auto = controller.Popover(page, "btn_popover_title")
    popover_auto.expect_active(False)
    popover_auto.set(True)
    popover_auto.expect_active(True)
    popover_auto.expect_body("Placement should be auto along with a title")
    popover_auto.expect_title("Popover title")
    popover_auto.expect_placement(
        "right"
    )  # since there is no space on the top, it defaults to right
    popover_auto.set(False)
    popover_auto.expect_active(False)

    popover_top = controller.Popover(page, "btn_popover_top")
    popover_top.expect_active(False)
    popover_top.set(True)
    popover_top.expect_active(True)
    popover_top.expect_body("Popover placement should be on the top")
    popover_top.expect_placement("top")
    popover_top.set(False)
    popover_top.expect_active(False)

    popover_right = controller.Popover(page, "btn_popover_right")
    popover_right.expect_active(False)
    popover_right.set(True)
    popover_right.expect_active(True)
    popover_right.expect_body("Popover placement should be on the right")
    popover_right.expect_placement("right")
    popover_right.set(False)
    popover_right.expect_active(False)

    popover_left = controller.Popover(page, "btn_popover_left")
    popover_left.expect_active(False)
    popover_left.set(True)
    popover_left.expect_active(True)
    popover_left.expect_body("Popover placement should be on the left")
    popover_left.expect_placement("left")
    popover_left.set(False)
    popover_left.expect_active(False)
