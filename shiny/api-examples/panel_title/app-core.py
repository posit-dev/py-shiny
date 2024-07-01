from shiny import App, Inputs, ui

app_ui = ui.page_fluid(ui.panel_title("Page title", "Window title"))


def server(input: Inputs):
    pass


app = App(app_ui, server)
