from conftest import ShinyAppProc
from controls import Accordion, AccordionPanel, InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def test_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    acc = Accordion(page, "acc")
    acc_panel_A = AccordionPanel(page, "acc", "Section A")
    output_txt_verbatim = OutputTextVerbatim(page, "acc_txt")
    alternate_button = InputActionButton(page, "alternate")
    open_all_button = InputActionButton(page, "open_all")
    close_all_button = InputActionButton(page, "close_all")
    toggle_b_button = InputActionButton(page, "toggle_b")
    toggle_updates_button = InputActionButton(page, "toggle_updates")
    toggle_efg_button = InputActionButton(page, "toggle_efg")
    acc.expect_width(None)
    acc.expect_height(None)

    # initial state - by default only A is open
    acc.expect_panels(["Section A", "Section B", "Section C", "Section D"])
    output_txt_verbatim.expect_value("input.acc(): ('Section A',)")
    acc.expect_open(["Section A"])
    acc_panel_A.expect_label("Section A")
    acc_panel_A.expect_body("Some narrative for section A")
    acc_panel_A.expect_open(True)

    alternate_button.click()
    acc.expect_open(["Section B", "Section D"])
    output_txt_verbatim.expect_value("input.acc(): ('Section B', 'Section D')")

    alternate_button.click()
    acc.expect_open(["Section A", "Section C"])
    output_txt_verbatim.expect_value("input.acc(): ('Section A', 'Section C')")

    open_all_button.click()
    acc.expect_open(["Section A", "Section B", "Section C", "Section D"])
    output_txt_verbatim.expect_value(
        "input.acc(): ('Section A', 'Section B', 'Section C', 'Section D')"
    )

    close_all_button.click()
    acc.expect_open([])
    acc.expect_open_panels_to_contain_text([])
    output_txt_verbatim.expect_value("input.acc(): None")

    toggle_b_button.click()
    acc.expect_open(["Section B"])
    output_txt_verbatim.expect_value("input.acc(): ('Section B',)")

    # check attributes for all panels before clicking on add/remove updates
    acc.expect_all_panels_to_have_attribute(
        "data-value", ["Section A", "Section B", "Section C", "Section D"]
    )
    acc_panel_updated_A = AccordionPanel(page, "acc", "updated_section_a")
    toggle_updates_button.click()
    acc_panel_updated_A.expect_label("Updated title")
    acc_panel_updated_A.expect_body("Updated body")
    acc_panel_updated_A.expect_icon("Look! An icon! -->")

    acc.expect_panels(["Section A", "Section B", "Section C", "Section D"])
    output_txt_verbatim.expect_value("input.acc(): ('updated_section_a', 'Section B')")

    toggle_efg_button.click()
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
    # output_txt_verbatim.expect_value(
    #     "input.acc(): ('updated_section_a', 'Section B', 'Section E', 'Section F', 'Section G')"
    # )
