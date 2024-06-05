from playwright.sync_api import Page

from shiny.playwright.controls import OutputTextVerbatim
from shiny.run import ShinyAppProc


def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:

    page.goto(local_app.url)

    OutputTextVerbatim(page, "all_txt").expect_value(
        "('a-3-flush', 'bx-3-first-flush', 'by-3-first-flush', 'bx-3-second-flush', "
        "'by-3-second-flush', 'c-3-flush', 'a-3-flushed', 'bx-3-first-flushed', "
        "'by-3-first-flushed', 'bx-3-second-flushed', 'by-3-second-flushed', "
        "'c-3-flushed')"
    )
    OutputTextVerbatim(page, "flush_txt").expect_value(
        "('a-3-flush', 'bx-3-first-flush', 'by-3-first-flush', 'bx-3-second-flush', "
        "'by-3-second-flush', 'c-3-flush')"
    )
    OutputTextVerbatim(page, "flushed_txt").expect_value(
        "('a-3-flushed', 'bx-3-first-flushed', 'by-3-first-flushed', "
        "'bx-3-second-flushed', 'by-3-second-flushed', 'c-3-flushed')"
    )
    # Session end messages have not flushed yet
    OutputTextVerbatim(page, "session_end_txt").expect_value("[]")
    page.reload()
    # Session end messages have flushed
    OutputTextVerbatim(page, "session_end_txt").expect_value(
        "['session ended - sync - test1', 'session ended - async - test2', 'session ended - async - test3', 'session ended - sync - test4']"
    )
