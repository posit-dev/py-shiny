from playwright.sync_api import Page, expect
from conftest import ShinyAppProc, create_doc_example_fixture
from controls import SelectInput

app = create_doc_example_fixture("input_select")


def test_input_select(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # get the current selected option and verify its as expected
    opt = SelectInput(page, "state").get_selected()
    assert opt == "NY"

    # check the output text
    output = page.locator("#value")
    expect(output).to_contain_text("NY")

    # select a different option - for ex: "CA"
    SelectInput(page, "state").select_option("CA")

    # check the output text updates to "CA"
    expect(output).to_contain_text("CA")

