from shiny.express import input, render, ui

with ui.accordion(id="acc"):
    for letter in "ABCDE":
        with ui.accordion_panel(f"Section {letter}"):
            f"Some narrative for section {letter}"


@render.code
def acc_val():
    return "input.acc(): " + str(input.acc())
