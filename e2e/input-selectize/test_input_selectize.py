import re

from playwright.sync_api import Page, expect
from conftest import ShinyAppProc, create_doc_example_fixture

app = create_doc_example_fixture("input_selectize")


def test_input_selectize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # check the output text contains "NY"
    output = page.locator("#value")
    expect(output).to_contain_text("NY")

    # Add another option - for ex: "CA"
    page.locator(".selectize-input").click()

    # Dropdown should be visible
    dropdown = page.locator(".selectize-dropdown")
    expect(dropdown).to_be_visible()

    # Click on one state from the dropdown
    page.locator(".selectize-dropdown-content .option[data-value='CA']").click()

    # (selectize input would show the added options on the fly)
    CA_selected = page.locator(".selectize-input .item[data-value='CA']")
    expect(CA_selected).to_be_visible()

    # click outside the dropdown box to close the dropdown menu
    page.keyboard.press("Escape")

    # Check the selected values from the input
    selected_items_2 = page.locator(".selectize-input .item")
    mylist = []
    for i in range(selected_items_2.count()):
        mylist.append(selected_items_2.nth(i).inner_text())

    assert mylist == ['NY', 'CA']

    # Check the output
    output = page.locator("#value")
    print("This inner text is" + str(output.inner_text()))
    expect(output).to_contain_text("('NY', 'CA')")






