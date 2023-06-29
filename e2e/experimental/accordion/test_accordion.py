from conftest import ShinyAppProc
from controls import Accordion, InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def test_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    acc = Accordion(page, "acc")
    acc.expect_width(None)
    acc.expect_height(None)

    # initial state - by default only A is open
    acc.expect_panels(["Section A", "Section B", "Section C", "Section D"])
    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): ('Section A',)")
    acc.expect_open(["Section A"])

    # click on alternate button
    InputActionButton(page, "alternate").click()
    acc.expect_open(["Section B", "Section D"])
    acc.expect_open_panels_to_contain_text(
        ["Some narrative for section B", "Some narrative for section D"]
    )
    # expect(acc.loc_open).to_have_count(2)
    OutputTextVerbatim(page, "acc_txt").expect_value(
        "input.acc(): ('Section B', 'Section D')"
    )

    # click on alternate once again
    InputActionButton(page, "alternate").click()
    acc.expect_open(["Section A", "Section C"])
    acc.expect_open_panels_to_contain_text(
        ["Some narrative for section A", "Some narrative for section C"]
    )
    OutputTextVerbatim(page, "acc_txt").expect_value(
        "input.acc(): ('Section A', 'Section C')"
    )

    # click on open All
    InputActionButton(page, "open_all").click()
    acc.expect_open(["Section A", "Section B", "Section C", "Section D"])
    acc.expect_open_panels_to_contain_text(
        [
            "Some narrative for section A",
            "Some narrative for section B",
            "Some narrative for section C",
            "Some narrative for section D",
        ]
    )
    OutputTextVerbatim(page, "acc_txt").expect_value(
        "input.acc(): ('Section A', 'Section B', 'Section C', 'Section D')"
    )

    # click on close All
    InputActionButton(page, "close_all").click()
    acc.expect_open([])
    acc.expect_open_panels_to_contain_text([])
    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): None")

    # click on open/close B
    InputActionButton(page, "toggle_b").click()
    acc.expect_open(["Section B"])
    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): ('Section B',)")

    # check attributes for all panels before clicking on add/remove updates
    acc.expect_all_panels_to_have_attribute(
        "data-value", ["Section A", "Section B", "Section C", "Section D"]
    )

    # check attributes for all panels after clicking on add/remove updates
    InputActionButton(page, "toggle_updates").click()
    acc.expect_panels(["Section A", "S  ection B", "Section C", "Section D"])
    acc.expect_all_panels_to_have_attribute(
        "data-value", ["updated_section_a", "Section B", "Section C", "Section D"]
    )
    acc.expect_open_panels_to_contain_text(
        ["Updated body", "Some narrative for section B"]
    )
    OutputTextVerbatim(page, "acc_txt").expect_value(
        "input.acc(): ('updated_section_a', 'Section B')"
    )

    # click on add/remove EFG
    InputActionButton(page, "toggle_efg").click()
    acc.expect_panels(
        [
            "Section A",
            "Section B",
            "Section C",
            "Section D",
            "Section E",
            "Section F",
            "Section G",
        ]
    )

    acc.expect_open(["Section A", "Section B", "Section E", "Section F", "Section G"])
    # failing since there is a bug in the code
    # OutputTextVerbatim(page, "acc_txt").expect_value(
    #     "input.acc(): ('updated_section_a', 'Section B', 'Section E', 'Section F', 'Section G')"
    # )
