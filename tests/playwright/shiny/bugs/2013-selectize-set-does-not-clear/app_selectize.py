from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_selectize(
        "test_selectize", "Select", ["Choice 1", "Choice 2"], multiple=True
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
