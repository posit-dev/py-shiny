import os
from shiny import *

app_ui = ui.page_fluid(
    ui.download_button("downloadData", "Download"),
)

# For more examples of different types of download handlers, see:
# https://github.com/rstudio/prism/blob/68ffc27/examples/download/app.py#L90
def server(input: Inputs, output: Outputs, session: Session):
    @session.download()
    def downloadData():
        return os.path.join(os.path.dirname(__file__), "mtcars.csv")


app = App(app_ui, server)
