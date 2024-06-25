from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    controller.OutputTextVerbatim(page, "no_output").expect_value("DATA SUMMARY")
    controller.OutputTextVerbatim(page, "no_parens").expect_value("DATA SUMMARY")
    controller.OutputTextVerbatim(page, "to_upper").expect_value("DATA SUMMARY")
    controller.OutputTextVerbatim(page, "to_lower").expect_value("data summary")
