from conftest import ShinyAppProc
from controls import OutputTextVerbatim
from playwright.sync_api import Page


def test_output_transformer(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    OutputTextVerbatim(page, "t1").expect_value("t1; no call; sync")
    OutputTextVerbatim(page, "t2").expect_value("t2; no call; async")
    OutputTextVerbatim(page, "t3").expect_value("t3; call; sync")
    OutputTextVerbatim(page, "t4").expect_value("t4; call; async")
    OutputTextVerbatim(page, "t5").expect_value("t5; call; sync; w/ extra_txt")
    OutputTextVerbatim(page, "t6").expect_value("t6; call; async; w/ extra_txt")
