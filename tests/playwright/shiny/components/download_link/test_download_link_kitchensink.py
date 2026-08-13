from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_download_link_kitchensink(
    page: Page, local_app: ShinyAppProc, tmp_path: Path
) -> None:
    page.goto(local_app.url)

    prefix_input = controller.InputText(page, "prefix")
    summary_toggle = controller.InputCheckbox(page, "include_summary")
    plain_link = controller.DownloadLink(page, "plain_link")
    styled_link = controller.DownloadLink(page, "styled_link")

    plain_link.expect_label("Plain report")
    styled_link.expect_label("Styled report")
    styled_link.expect_width("560px")

    with page.expect_download() as plain_info:
        plain_link.click()
    plain_download = plain_info.value
    assert plain_download.suggested_filename == "report-plain.txt"
    plain_path = tmp_path / plain_download.suggested_filename
    plain_download.save_as(plain_path)
    plain_content = plain_path.read_text()
    assert "report plain download #1" in plain_content
    assert "Summary: plain link" in plain_content

    prefix_input.set("custom")
    summary_toggle.set(False)

    with page.expect_download() as styled_info:
        styled_link.click()
    styled_download = styled_info.value
    assert styled_download.suggested_filename == "custom-styled.csv"
    styled_path = tmp_path / styled_download.suggested_filename
    styled_download.save_as(styled_path)
    styled_content = styled_path.read_text()
    assert "metric,value" in styled_content
    assert "prefix,custom" in styled_content
    assert "download_count,1" in styled_content
    assert "footer,enabled" not in styled_content

    summary_toggle.set(True)

    with page.expect_download() as plain_info_2:
        plain_link.click()
    plain_download_2 = plain_info_2.value
    assert plain_download_2.suggested_filename == "custom-plain.txt"
    plain_path_2 = tmp_path / plain_download_2.suggested_filename
    plain_download_2.save_as(plain_path_2)
    plain_content_2 = plain_path_2.read_text()
    assert "custom plain download #2" in plain_content_2
    assert "Summary: plain link" in plain_content_2
