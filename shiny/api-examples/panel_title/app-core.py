from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(ui.panel_title("Page title", "Window title"))


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
