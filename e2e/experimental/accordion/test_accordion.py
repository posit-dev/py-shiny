from conftest import ShinyAppProc
from controls import Accordion, AccordionPanel, InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def test_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    acc = Accordion(page, "acc")
    acc_panel_A = AccordionPanel(page, "acc", "Section A")
    acc.expect_width(None)
    acc.expect_height(None)

    # initial state - by default only A is open
    acc.expect_panels(["Section A", "Section B", "Section C", "Section D"])
    OutputTextVerbatim(page, "acc_txt").expect_value("input.acc(): ('Section A',)")
    acc.expect_open(["Section A"])
    acc_panel_A.expect_label("Section A")
    acc_panel_A.expect_body("Some narrative for section A")
    acc_panel_A.expect_open()

    # click on alternate button
    InputActionButton(page, "alternate").click()
    acc.expect_open(["Section B", "Section D"])
    OutputTextVerbatim(page, "acc_txt").expect_value(
        "input.acc(): ('Section B', 'Section D')"
    )

    # click on alternate once again
    InputActionButton(page, "alternate").click()
    acc.expect_open(["Section A", "Section C"])
    OutputTextVerbatim(page, "acc_txt").expect_value(
        "input.acc(): ('Section A', 'Section C')"
    )

    # click on open All
    InputActionButton(page, "open_all").click()
    acc.expect_open(["Section A", "Section B", "Section C", "Section D"])
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
    acc_panel_updated_A = AccordionPanel(page, "acc", "updated_section_a")
    # check attributes for all panels after clicking on add/remove updates
    InputActionButton(page, "toggle_updates").click()
    acc_panel_updated_A.expect_label("Updated title")
    acc_panel_updated_A.expect_body("Updated body")
    acc_panel_updated_A.expect_icon("Look! An icon! -->")

    acc.expect_panels(["Section A", "Section B", "Section C", "Section D"])
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
    # will be uncommented once https://github.com/rstudio/bslib/issues/565 is fixed
    # OutputTextVerbatim(page, "acc_txt").expect_value(
    #     "input.acc(): ('updated_section_a', 'Section B', 'Section E', 'Section F', 'Section G')"
    # )
