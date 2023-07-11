from conftest import ShinyAppProc, create_doc_example_fixture
from controls import InputFile
from playwright.sync_api import FilePayload, Page, expect

app = create_doc_example_fixture("input_file")


def test_input_file_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    file1 = InputFile(page, "file1")
    # file1.expect.to_have_value("Data summary")
    # expect(file1.loc).to_have_value("Data summary")

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

    file1.set(file_info)

    expect(file1.loc_file_display).to_have_value(file_info.get("name"))

    file1.expect_complete()

    # TODO-barret; Test UI output to not be empty
