from __future__ import annotations

from conftest import ShinyAppProc
from controls import InputFile, OutputTable, OutputTextVerbatim
from playwright.sync_api import FilePayload, Page, expect


def test_input_file_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    file1 = InputFile(page, "file1")

    expect(file1.loc_label).to_have_text("Choose CSV File")
    expect(file1.loc_button).to_have_text("Browse...")

    file1.expect_accept([".csv"])
    file1.expect_button_label("Browse...")
    file1.expect_capture(None)
    # file1.expect_files(None)
    file1.expect_label("Choose CSV File")
    file1.expect_multiple(False)
    file1.expect_placeholder("No file selected")
    file1.expect_width(None)

    file_info: FilePayload = {
        "name": "mtcars.csv",
        "mimeType": "text/csv",
        # from plotnine.data import mtcars
        # mtcars.loc[0:3, mtcars.columns[0:4]].to_csv()
        "buffer": b",name,mpg,cyl,disp\n0,Mazda RX4,21.0,6,160.0\n1,Mazda RX4 Wag,21.0,6,160.0\n2,Datsun 710,22.8,4,108.0\n3,Hornet 4 Drive,21.4,6,258.0\n",
    }
    file_info2 = file_info.copy()
    file_info2["name"] = "mtcars2.csv"

    file1.set(file_info)
    expect(file1.loc_file_display).to_have_value(file_info.get("name"))

    file1.expect_complete()

    output_table = OutputTable(page, "summary")

    output_table.expect_column_labels(["Row Count", "Column Count", "Column Names"])
    output_table.expect_n_row(1)

    file2 = InputFile(page, "file2")
    file2.set([file_info, file_info2])
    expect(file2.loc_file_display).to_have_value("2 files")
    OutputTextVerbatim(page, "file2_info").expect_value(
        """File name: mtcars.csv
File type: text/csv
File size: 129 bytes
---
File name: mtcars2.csv
File type: text/csv
File size: 129 bytes
"""
    )
    # file2.expect_files([file_info, file_info])
