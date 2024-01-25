from shiny import reactive
from shiny.express import input, ui

with ui.card():
    ui.input_action_button("set_acc", "Only open sections A,C,E", class_="mt-3 mb-3")
    # Provide an id to create a shiny input binding
    with ui.accordion(id="acc", open=["Section B", "Section D"], multiple=True):
        for letter in "ABCDE":
            with ui.accordion_panel(f"Section {letter}"):
                f"Some narrative for section {letter}"


@reactive.Effect
@reactive.event(input.set_acc)
def open_panels():
    ui.update_accordion("acc", show=["Section A", "Section C", "Section E"])
