from pathlib import Path

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_streaming_download_updates_outputs_and_handles_input(
    page: Page, local_app: ShinyAppProc, tmp_path: Path
) -> None:
    page.goto(local_app.url)
    status = controller.OutputText(page, "status")
    status.expect_value("idle")

    with page.expect_download() as info:
        controller.DownloadButton(page, "dl").click()
        # A value set mid-stream reaches the page while the download is open.
        status.expect_value("streaming")
        # The session handles this click while the stream waits on it.
        controller.InputActionButton(page, "release").click()
        status.expect_value("done")

    path = tmp_path / "streamed.txt"
    info.value.save_as(path)
    assert path.read_text() == "first,second"
