from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_accordion_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    accordion1 = controller.Accordion(page, "accordion_1")
    accordion1.expect_width("600px")
    accordion1.expect_height("300px")
    accordion1.expect_class("bg-light")
    accordion1.expect_multiple(False)
    accordion1_panel1 = accordion1.accordion_panel("panel1")
    accordion1_panel1.expect_open(True)
    accordion1_panel1.expect_label("Panel 1")
    accordion1_panel1.expect_icon(False)

    accordion1_panel2 = accordion1.accordion_panel("panel2")
    accordion1_panel2.expect_open(False)
    accordion1_panel2.expect_label("Panel 2")
    accordion1_panel2.expect_icon(True)
    accordion1_panel2.set(True)
    accordion1_panel2.expect_open(True)
    accordion1_panel1.expect_open(False)

    accordion2 = controller.Accordion(page, "accordion_2")
    accordion2.expect_width(None)
    accordion2.expect_height(None)
    accordion2.expect_multiple(True)

    accordion2_panel3 = accordion2.accordion_panel("panel3")
    accordion2_panel3.expect_open(True)

    accordion2_panel4 = accordion2.accordion_panel("panel4")
    accordion2_panel4.expect_open(False)
    accordion2_panel4.set(True)
    accordion2_panel4.expect_open(True)
    accordion2_panel3.expect_open(True)
