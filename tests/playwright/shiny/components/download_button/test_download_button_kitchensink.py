from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_download_button_kitchensink(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    increment = controller.InputActionButton(page, "increment")
    plain_button = controller.DownloadButton(page, "plain_csv")
    styled_button = controller.DownloadButton(page, "styled_csv")
    plain_button.expect_label("Plain CSV")
    styled_button.expect_label("Styled CSV")
    styled_button.expect_width("560px")

    with page.expect_download() as plain_info:
        plain_button.click()
    plain_download = plain_info.value
    plain_path_str = plain_download.path()
    assert plain_download.suggested_filename == "plain-1.csv"
    assert plain_path_str is not None
    assert Path(plain_path_str).read_text() == "kind,inventory,count\nplain,0,1\n"

    increment.click()

    with page.expect_download() as styled_info:
        styled_button.click()
    styled_download = styled_info.value
    styled_path_str = styled_download.path()
    assert styled_path_str is not None
    assert styled_download.suggested_filename == "styled-1-1.csv"
    assert (
        Path(styled_path_str).read_text()
        == "metric,value\ninventory,1\ndownload_number,1\n"
    )

    increment.click()

    with page.expect_download() as plain_info_2:
        plain_button.click()
    plain_download_2 = plain_info_2.value
    plain_path_str_2 = plain_download_2.path()
    assert plain_path_str_2 is not None
    assert plain_download_2.suggested_filename == "plain-2.csv"
    assert Path(plain_path_str_2).read_text() == "kind,inventory,count\nplain,2,2\n"
