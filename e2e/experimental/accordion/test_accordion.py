from conftest import ShinyAppProc
from controls import Accordion, InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def test_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    acc = Accordion(page, "acc")
    acc.expect_width(None)
    acc.expect_height(None)
    acc.expect_panels(["Section A", "Section B", "Section C", "Section D"])
    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): ('Section A',)")
    acc.expect_open(["Section A"])

    InputActionButton(page, "alternate").click()
    acc.expect_open(["Section A", "Section C"])
    # expect(acc.loc_open).to_have_count(2)
    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): ('Section B', 'Section D')")

    InputActionButton(page, "alternate").click()
    acc.expect_open(["Section B", "Section D"])

    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): ('Section A', 'Section C')")
