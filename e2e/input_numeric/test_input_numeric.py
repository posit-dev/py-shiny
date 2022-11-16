# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

import controls
from conftest import ShinyAppProc, create_doc_example_fixture
from playground import NumericInputDos
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_numeric")


# def shinypage(page: Page) -> Page:
#     # look up the pytest.mark.shinyapp, throw if it's not there
#     # Use conftest's run_shiny_app to start the app
#     with run_shiny_app(...) as app:
#         if navigate:
#             page.goto(app.url)
#         yield page
#
#
# @pytest.mark.shinyapp(example="input_numeric", navigate=False)
# def test_input_numeric_tmp(shinypage: Page) -> None:
#     ...


def test_dos_input(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    obs = NumericInputDos(page, "obs")
    obs.expect.to_have_value("10")
    expect(obs.loc).to_have_value("10")

    expect(obs.loc_label).to_have_text("Observations")

    # Bad approach
    assert obs.value == 10, "value is 10"
    assert obs.value_min == "1", "value_min is 1"
    assert obs.value_max == "100", "value_max is 100"
    assert type(obs.value_step) is None, "value_step is None"

    # Better approach
    expect(obs.loc).to_have_value("10")
    expect(obs.loc).to_have_attribute("min", "1")
    expect(obs.loc).to_have_attribute("max", "100")
    # Can not test for the absence of something when waiting is involved
    # expect(obs.loc).not_to_have_attribute("step")

    # Best approach
    obs.expect_min_to_have_value("1")
    obs.expect_max_to_have_value("100")
    obs.expect_step_to_have_value(None)
    obs.expect_width_to_have_value(None)


def test_dos_input_2(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    obs = NumericInputDos(page, "obs")
    obs.expect.to_have_value("10")
    obs.loc.fill("42")
    obs.expect.not_to_have_value("10")
    obs.expect.to_have_value("42")

    expect(obs.loc).to_have_value("42")


def test_input_numeric(page: Page, app: ShinyAppProc) -> None:
    # with page and app:
    page.goto(app.url)

    NumericInputDos(page, "obs").expect.to_have_value("0")
    # expect(NumericInputDos(page, "obs").loc).to_have_value("0")

    obs = controls.NumericInput(page, "obs")
    # obs.label.expect.to_have_text("Observed")
    obs.expect.to_have_value("10")

    output = page.locator("#value")
    expect(output).to_have_text("10")

    obs.loc.fill("21")
    obs.expect.to_have_value("21")
    expect(output).to_have_text("21")
