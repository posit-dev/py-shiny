# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

import controls
from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_numeric")


def test_input_numeric(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    obs = controls.NumericInput(page, "obs")
    obs.expect.to_have_value("10")
    output = page.locator("#value")
    expect(output).to_have_text("10")

    obs.loc.fill("21")
    obs.expect.to_have_value("21")
    expect(output).to_have_text("21")
