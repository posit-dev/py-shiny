import controls
from conftest import ShinyAppProc
from playwright.sync_api import Page, expect

def test_file_upload(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    input_file = "mtcars.csv"

    file_input = controls.FileInput(page, "file1-label")
    file_input.upload_file(input_file)

    upload_status = file_input.loc.locator(".progress-bar").inner_text()
    assert upload_status == "Upload complete"

    file_output = page.locator("#file_content.shiny-bound-output")
    expect(file_output).to_contain_text(input_file)
    expect(file_output).to_contain_text("MIME type: text/csv")



