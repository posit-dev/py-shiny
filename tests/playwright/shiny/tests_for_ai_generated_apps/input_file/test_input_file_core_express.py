from playwright.sync_api import FilePayload, Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_file_input_demo(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test file input component
    file_input = controller.InputFile(page, "file1")

    # Test initial state
    file_input.expect_label("Upload File")
    file_input.expect_multiple(True)
    file_input.expect_accept(
        [".csv", ".txt", "text/plain", "application/pdf", "image/*"]
    )
    file_input.expect_button_label("Choose Files...")
    file_input.expect_width("400px")
    file_input.expect_capture("user")

    # Test data frame output initial state
    file_table = controller.OutputDataFrame(page, "file_table")
    file_table.expect_column_labels(["Name", "Size (bytes)", "Type"])
    file_table.expect_nrow(0)
    file_table.expect_ncol(3)

    # Note: The file content is a CSV with a header and some data
    # Simulate uploading a CSV file
    file_info: FilePayload = {
        "name": "users.csv",
        "mimeType": "text/csv",
        "buffer": b',user_id,name,email\n1,Alice,alice@example.com\n2,"Bob, Los Angeles", bob\n',
    }

    file_input.set(file_info)
    file_input.expect_complete()

    # After upload, check if table is updated
    file_table.expect_nrow(1)  # Should show one row for the uploaded file
    file_table.expect_ncol(3)  # Should still have 3 columns

    # simulate uploading multiple files
    file_info2 = file_info.copy()
    file_info2["name"] = "users2.csv"
    file_info2["buffer"] = (
        b",user_id,name,email\n3,Charlie,charlie@example.com\n4,Dave,dave@example.com\n"
    )
    file_input.set([file_info, file_info2])
    file_input.expect_complete()

    # After uploading multiple files, check if table is updated
    file_table.expect_nrow(2)  # Should show two rows for the uploaded files
    file_table.expect_ncol(3)  # Should still have 3 columns
