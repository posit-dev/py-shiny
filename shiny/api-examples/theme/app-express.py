from shared import filler_text, my_theme

from shiny.express import input, render, ui

ui.page_opts(
    title="Theme Example",
    theme=my_theme,
)

with ui.sidebar(title="Parameters"):
    ui.input_numeric("n", "N", min=0, max=100, value=20)
    ui.input_slider("m", "M", min=0, max=100, value=50)
    ui.input_selectize("letter", "Letter", choices=["A", "B", "C"])

ui.h2("Output")


@render.code
def txt():
    return f"n*2 is {input.n() * 2}"


ui.markdown(filler_text)
