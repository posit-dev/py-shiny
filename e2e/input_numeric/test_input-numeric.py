from conftest import ShinyAppProc, create_doc_example_fixture
from playground import InputNumeric
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_numeric")


def test_input_numeric(page: Page, app: ShinyAppProc) -> None:
    # with page and app:
    page.goto(app.url)

    obs = InputNumeric(page, "obs")
    # obs.label.expect.to_have_text("Observed")
    obs.expect.to_have_value("10")

    output = page.locator("#value")
    expect(output).to_have_text("10")

    obs.loc.fill("21")
    obs.expect.to_have_value("21")
    expect(output).to_have_text("21")
