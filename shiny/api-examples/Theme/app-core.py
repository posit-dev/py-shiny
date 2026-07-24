from shared import filler_text, my_theme

from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_numeric("n", "N", min=0, max=100, value=20),
        ui.input_slider("m", "M", min=0, max=100, value=50),
        ui.input_selectize("letter", "Letter", choices=["A", "B", "C"]),
        title="Parameters",
    ),
    ui.h2("Output"),
    ui.output_text_verbatim("txt"),
    ui.markdown(filler_text),
    title="Theme Example",
    theme=my_theme,
)


def server(input, output, session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


app = App(app_ui, server)
