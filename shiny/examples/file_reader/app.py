import pandas as pd
from htmltools import HTML
from shiny import *

app_ui = ui.page_fluid(ui.output_ui("result"), class_="p-3")


@reactive.file_reader("mtcars.csv")
def read_file():
    return pd.read_csv("mtcars.csv")


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render.render_ui()
    def result():
        return HTML(
            read_file().to_html(
                index=False, border=None, classes="table table-bordered w-auto"
            )
        )


app = App(app_ui, server)
