from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_output_transformer(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    controller.OutputTextVerbatim(page, "t1").expect_value("t1; no call; sync")
    controller.OutputTextVerbatim(page, "t2").expect_value("t2; no call; async")
    controller.OutputTextVerbatim(page, "t3").expect_value("t3; call; sync")
    controller.OutputTextVerbatim(page, "t4").expect_value("t4; call; async")
    controller.OutputTextVerbatim(page, "t5").expect_value(
        "t5; call; sync; w/ extra_txt"
    )
    controller.OutputTextVerbatim(page, "t6").expect_value(
        "t6; call; async; w/ extra_txt"
    )
