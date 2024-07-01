from shiny import App, Inputs, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("obs", "Observations:", 10, min=1, max=100),
    ui.output_text_verbatim("value"),
)


def server(input: Inputs):
    @render.text
    def value():
        return input.obs()


app = App(app_ui, server)
