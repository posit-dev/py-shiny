from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_numeric")


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


def test_input_numeric_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    obs = controller.InputNumeric(page, "obs")
    obs.expect.to_have_value("10")
    expect(obs.loc).to_have_value("10")

    expect(obs.loc_label).to_have_text("Observations:")

    obs.expect_label("Observations:")
    obs.expect_value("10")
    obs.expect_min("1")
    obs.expect_max("100")
    obs.expect_step(None)
    obs.expect_width(None)


def test_input_numeric_typical(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # page.set_default_timeout(1000)

    obs = controller.InputNumeric(page, "obs")
    obs.expect.to_have_value("10")
    obs.loc.fill("42")
    obs.expect.not_to_have_value("10")
    obs.expect.to_have_value("42")

    expect(obs.loc).to_have_value("42")


def test_input_numeric_app(page: Page, app: ShinyAppProc) -> None:
    # with page and app:
    page.goto(app.url)

    obs = controller.InputNumeric(page, "obs")
    # obs.label.expect.to_have_text("Observed")
    obs.expect.to_have_value("10")

    value = controller.OutputTextVerbatim(page, "value")
    value.expect_value("10")

    output = page.locator("#value")
    expect(output).to_have_text("10")

    obs.loc.fill("21")
    obs.expect.to_have_value("21")
    value.expect_value("21")
