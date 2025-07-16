from shiny.express import expressify, input, render, ui


@expressify
def my_accordion(**kwargs):
    with ui.accordion(**kwargs):
        for letter in "ABCDE":
            with ui.accordion_panel(f"Section {letter}"):
                f"Some narrative for section {letter}"


ui.markdown("#### Single-select accordion")

my_accordion(multiple=False, id="acc_single")


@render.code
def acc_single_val():
    return "input.acc_single(): " + str(input.acc_single())


ui.br()

ui.markdown("#### Multi-select accordion")

my_accordion(multiple=True, id="acc_multiple")


@render.code
def acc_multiple_val():
    return "input.acc_multiple(): " + str(input.acc_multiple())
