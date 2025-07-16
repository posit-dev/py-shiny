from shiny.express import input, render, ui

ui.page_opts(theme=ui.Theme.from_brand(__file__))

ui.input_slider("n", "N", 0, 100, 20)


@render.code
def txt():
    return f"n*2 is {input.n() * 2}"
