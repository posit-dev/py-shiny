# Ref: https://playwright.dev/python/docs/downloads

from controls import DownloadButton
from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page
from pathlib import Path

from datetime import date
from re import search
import hashlib


app1 = create_doc_example_fixture("download")
app2 = create_doc_example_fixture("download_link")


def verify_download(page: Page, downloadBtnId: str, fileName: str):
    download_btn = DownloadButton(page, downloadBtnId)

    with page.expect_download() as download_info:
        download_btn.loc.click()

    download= download_info.value

    file_path = f"e2e/file-download/{fileName}"

    # Check for debugging purpose only
    if download_info.is_done():
        print("TRUE: DOWNLOAD IS SUCCESSFUL")
    else:
        print("FALSE: DOWNLOAD IS NOT SUCCESSFUL")

    download.save_as(file_path)

    # check md5 sum of the file
    md5_hash = generate_md5(file_path)

    if search("mtcars", fileName):
        assert md5_hash == "a99833f538af72039f98a04575558789"
    elif search("新型-", fileName):
        assert md5_hash == "f1767ee79c58e196e9f1f9776d90fb7f"
    else:
        print("md5 does not match which is expected for Random scatter plot " + fileName)

#def generate_md5(file: Union[PurePath, str]):
def generate_md5(file: Path):
    with open(file, "rb") as f:
        bytes = f.read()  # read file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest()

    return readable_hash

def test_download_button(page: Page, app1: ShinyAppProc) -> None:
    page.goto(app1.url)
    verify_download(page, "download1", "mtcars.csv")
    verify_download(page, "download2", "image.png")
    verify_download(page, "download3", f"新型-{date.today().isoformat()}.csv")

    #TODO: Check download link

# def test_download_link(page: Page, app2: ShinyAppProc) -> None:
#     page.goto(app2.url)
      #TODO: Check the download failure cases
      #verify_download(page, "download4", "failurestest.txt") # Failed - Network error
      #verify_download(page, "download5", "missing_download.json") # Failed - No file

