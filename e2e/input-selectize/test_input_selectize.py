from playwright.sync_api import Page, expect
from conftest import ShinyAppProc, create_doc_example_fixture
from controls import SelectizeInput

app = create_doc_example_fixture("input_selectize")


def test_input_selectize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # check the output text contains "NY"
    output = page.locator("#value")
    expect(output).to_contain_text("NY")

    # Create an object to represent the widget
    selectize = SelectizeInput(page, "state")

    selectize.select_option("CA")

    # Check the selected values from the input
    options = selectize.get_selected_items()

    assert options == ['NY', 'CA']

    # Check the output
    output = page.locator("#value")
    expect(output).to_contain_text("('NY', 'CA')")


