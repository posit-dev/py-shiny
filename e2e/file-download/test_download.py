# Ref: https://playwright.dev/python/docs/downloads

from controls import DownloadButton
from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page

from datetime import date
import numpy as np


app1 = create_doc_example_fixture("download")
#app2 = create_doc_example_fixture("download_button")
app2 = create_doc_example_fixture("download_link")


def verify_download(page: Page, downloadBtnId: str, fileName: str):
    download_btn = DownloadButton(page, downloadBtnId)

    with page.expect_download() as download_info:
        download_btn.loc.click()

    download= download_info.value

    if download_info.is_done():
        print("TRUE: DOWNLOAD IS SUCCESSFUL")
    else:
        print("FALSE: DOWNLOAD IS NOT SUCCESSFUL")

    download.save_as(f"e2e/file-download/{fileName}")



def test_download_button(page: Page, app1: ShinyAppProc) -> None:
    page.goto(app1.url)
    verify_download(page, "download1", "mtcars.csv")
    verify_download(page, "download2", "image.png")
    verify_download(page, "download3", f"新型-{date.today().isoformat()}.csv")

    #TODO: Check the download failure cases
    #TODO: Check download link



# def test_download_link(page: Page, app2: ShinyAppProc) -> None:
#     page.goto(app2.url)
