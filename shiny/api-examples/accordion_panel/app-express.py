from shiny.express import input, render, ui

ui.card_header("Single selection accordion")
with ui.accordion(multiple=False, id="acc"):
    for letter in "ABCDE":
        with ui.accordion_panel(f"Section {letter}"):
            f"Some narrative for section {letter}"


@render.text
def acc_val():
    return "input.acc(): " + str(input.acc())
