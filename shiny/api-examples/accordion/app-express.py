from shiny import reactive
from shiny.express import input, render, ui

with ui.card():
    ui.card_header("Single selction accordion")
    with ui.accordion(multiple=False, id="acc_single"):
        with ui.accordion_panel("Section 1"):
            "Some text for Section 1"
        with ui.accordion_panel("Section 2"):
            "More things on Section 2"
        with ui.accordion_panel("Section 3"):
            "Another great section"

    @render.text
    def acc_single_val():
        return "Selected accordion: " + str(input.acc_single())


with ui.card():
    ui.card_header("Multiple selction accordion")
    with ui.accordion(multiple=True, id="acc_multiple"):
        with ui.accordion_panel("Section 1"):
            "Some text for Section 1"
        with ui.accordion_panel("Section 2"):
            "More things on Section 2"
        with ui.accordion_panel("Section 3"):
            "Another great section"

    @render.text
    def acc_multiple_val():
        return "Selected accordions: " + str(input.acc_multiple())
