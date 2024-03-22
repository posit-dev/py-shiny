from conftest import ShinyAppProc
from controls import OutputTextVerbatim
from playwright.sync_api import Page


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

    # Verify `on_ended` callbacks are called in the correct order (and cancelled)
    local_app.close()

    # Wait up to 3 seconds for the app to close and print the logs. (Should be ~ instant)
    local_app.stdout.wait_for(lambda x: "test4" in x, 3)
    stdout = str(local_app.stdout)
    out_indexes = [
        stdout.index("session ended - sync - test1"),
        stdout.index("session ended - async - test2"),
        stdout.index("session ended - async - test3"),
        stdout.index("session ended - sync - test4"),
    ]
    for i in range(len(out_indexes)):
        index = out_indexes[i]
        assert index >= 0
        # Make sure they are ordered correctly
        if i > 0:
            prev_index = out_indexes[i - 1]
            assert index > prev_index
