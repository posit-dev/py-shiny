from shiny import App, Inputs, render, ui

app_ui = ui.page_fluid(
    ui.input_switch("somevalue", "Some value", False),
    ui.output_text("value"),
)


def server(input: Inputs):
    @render.text
    def value():
        return input.somevalue()


app = App(app_ui, server)
