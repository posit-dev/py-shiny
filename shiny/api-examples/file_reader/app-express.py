import pathlib

import pandas as pd

from shiny import reactive
from shiny.express import render

file = pathlib.Path(__file__).parent / "mtcars.csv"


@reactive.file_reader(file)
def read_file():
    return pd.read_csv(file)


@render.table
def result():
    return read_file()
