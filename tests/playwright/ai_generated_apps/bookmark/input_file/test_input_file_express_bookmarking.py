from playwright.sync_api import FilePayload, Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_file_input_bookmarking(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test file input component
    file_input = controller.InputFile(page, "basic")
    mod_file_input = controller.InputFile(page, "first-module_file")

    file_output_txt = controller.OutputText(page, "basic_text")
    mod_file_output_txt = controller.OutputText(page, "first-mod_text")

    mod_file_output_txt.expect_value("No files selected")
    file_output_txt.expect_value("No files selected")

    # Note: The file content is a CSV with a header and some data
    # Simulate uploading a CSV file
    file_info: FilePayload = {
        "name": "users.csv",
        "mimeType": "text/csv",
        "buffer": b',user_id,name,email\n1,Alice,alice@example.com\n2,"Bob, Los Angeles", bob\n',
    }

    file_input.set(file_info)
    file_input.expect_complete()

    file_output_txt.expect_value("File name(s): users.csv")

    # simulate uploading multiple files
    file_info2 = file_info.copy()
    file_info2["name"] = "users2.csv"
    file_info2["buffer"] = (
        b",user_id,name,email\n3,Charlie,charlie@example.com\n4,Dave,dave@example.com\n"
    )
    mod_file_input.set([file_info, file_info2])
    file_input.expect_complete()

    mod_file_output_txt.expect_value("File name(s): users.csv, users2.csv")

    # click bookmark button
    bookmark_button = controller.InputBookmarkButton(page)
    bookmark_button.click()

    page.reload()

    # Check if the values are retained after reloading the page
    file_output_txt.expect_value("File name(s): users.csv")
    mod_file_output_txt.expect_value("File name(s): users.csv, users2.csv")
