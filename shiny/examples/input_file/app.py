import pandas as pd

from shiny import *
from shiny import experimental as x
from shiny.types import FileInfo

app_ui = ui.page_fluid(
    x.ui.layout_sidebar(
        x.ui.sidebar(
            ui.input_file("file1", "Choose CSV File", accept=[".csv"], multiple=False),
            ui.input_checkbox("header", "Header", True),
        ),
        ui.output_ui("contents"),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def contents():
        if input.file1() is None:
            return "Please upload a csv file"
        f: list[FileInfo] = input.file1()
        df = pd.read_csv(f[0]["datapath"], header=0 if input.header() else None)
        return ui.HTML(df.to_html(classes="table table-striped"))


app = App(app_ui, server)
