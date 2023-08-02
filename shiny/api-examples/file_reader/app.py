import pathlib

import pandas as pd

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

dir = pathlib.Path(__file__).parent

app_ui = ui.page_fluid(ui.output_table("result"), class_="p-3")


@reactive.file_reader(dir / "mtcars.csv")
def read_file():
    return pd.read_csv(dir / "mtcars.csv")


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.table
    def result():
        return read_file()


app = App(app_ui, server)
