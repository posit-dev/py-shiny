import os

import pytest
from conftest import ShinyAppProc
from controls import OutputTextVerbatim
from playwright.sync_api import Page

on_ci = os.environ.get("CI", "False") == "true"


def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:

    if on_ci:
        # 2024-03-22: The tests pass locally, but do not pass on CI. It started with
        # https://github.com/posit-dev/py-shiny/commit/2f75a9076c567690f2a6a647ec07cfa9e558ff9c
        # , but the changes in that commit were unrelated. We had believe it was an
        # update in uvicorn, but removing all other debug statements did not fix the
        # issue.
        # 2024-03-22 Barret: When inspecting the issue, we found that many log
        # INFO entries have different port values. This is concerning.
        # https://github.com/posit-dev/py-shiny/pull/1236
        pytest.skip("Error with stdout / stderr on CI. Related #1236")

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
