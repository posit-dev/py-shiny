import os
from shiny import *

js_file = os.path.join(os.path.dirname(__file__), "js/app.js")

app_ui = ui.page_fluid(
    "If you see this page before 'OK'-ing the alert box, something went wrong",
    ui.include_javascript(js_file),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
