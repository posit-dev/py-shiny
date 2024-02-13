import pytest
from conftest import ShinyAppProc
from controls import Accordion, InputActionButton, OutputTextVerbatim
from examples.example_apps import reruns, reruns_delay
from playwright.sync_api import Page


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_accordion(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    acc = Accordion(page, "acc")
    acc_panel_A = acc.accordion_panel("Section A")
    output_txt_verbatim = OutputTextVerbatim(page, "acc_txt")
    alternate_button = InputActionButton(page, "alternate")
    open_all_button = InputActionButton(page, "open_all")
    close_all_button = InputActionButton(page, "close_all")
    toggle_b_button = InputActionButton(page, "toggle_b")
    toggle_updates_button = InputActionButton(page, "toggle_updates")
    toggle_efg_button = InputActionButton(page, "toggle_efg")

    output_txt_verbatim.expect_value("input.acc(): ('Section A',)")

    acc_panel_A.set(True)
    acc_panel_A.expect_open(True)
    acc_panel_A.set(False)
    acc_panel_A.expect_open(False)

    acc.expect_width(None)
    acc.expect_height(None)

    close_all_button.click()
    acc.expect_open([])
    output_txt_verbatim.expect_value("input.acc(): None")
    acc.set(["Section A"])

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

    toggle_b_button.click()
    acc.expect_open(["Section A", "Section C", "Section D"])
    output_txt_verbatim.expect_value(
        "input.acc(): ('Section A', 'Section C', 'Section D')"
    )

    acc_panel_updated_A = acc.accordion_panel("updated_section_a")
    toggle_updates_button.click()
    acc_panel_updated_A.expect_label("Updated title")
    acc_panel_updated_A.expect_body("Updated body")
    acc_panel_updated_A.expect_icon("Look! An icon! -->")

    acc.expect_panels(["updated_section_a", "Section B", "Section C", "Section D"])
    # workaround - toggle it twice Section A
    acc_panel_updated_A.toggle()
    # add timeout to wait for css animation
    page.wait_for_timeout(100)
    acc_panel_updated_A.toggle()
    output_txt_verbatim.expect_value(
        "input.acc(): ('updated_section_a', 'Section C', 'Section D')"
    )

    # TODO-karan-future; Remove return when test is able to pass. Currently it hangs indefinitely and no notification as to why.
    return

    toggle_efg_button.click()
    acc.expect_panels(
        [
            "updated_section_a",
            "Section B",
            "Section C",
            "Section D",
            "Section E",
            "Section F",
            "Section G",
        ]
    )
    acc.expect_open(
        [
            "updated_section_a",
            "Section C",
            "Section D",
            "Section E",
            "Section F",
            "Section G",
        ]
    )
    # Should be uncommented once https://github.com/rstudio/bslib/issues/565 is fixed
    # output_txt_verbatim.expect_value(
    #     "input.acc(): ('updated_section_a', 'Section B', 'Section E', 'Section F', 'Section G')"
    # )
