import os
from shiny import *

css_file = os.path.join(os.path.dirname(__file__), "css/styles.css")

app_ui = ui.page_fluid(
    "Almost before we knew it, we had left the ground!!!",
    ui.include_css(css_file, method="link_files"),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
