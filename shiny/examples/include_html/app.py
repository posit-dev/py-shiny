from shiny import *

app_ui = ui.page_fluid()


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
