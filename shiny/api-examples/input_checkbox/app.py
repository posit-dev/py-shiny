from shiny import App, Inputs, render, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("somevalue", "Some value", False),
    ui.output_ui("value"),
)


def server(input: Inputs):
    @render.ui
    def value():
        return input.somevalue()


app = App(app_ui, server)
