from shared import filler_text

from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_numeric("n", "N", min=0, max=100, value=20),
        title="Parameters",
    ),
    ui.h2("Output"),
    ui.output_text_verbatim("txt"),
    ui.markdown(filler_text),
    title="Theme Example",
    theme="https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/sketchy/bootstrap.min.css",
)


def server(input, output, session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


app = App(app_ui, server)
