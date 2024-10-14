from datetime import datetime

import htmltools
import pandas as pd
import polars as pl

from shiny.express import render, ui

DATA = {
    "num": [1, 2],
    "chr": ["a", "b"],
    "cat": ["a", "a"],
    "dt": [datetime(2000, 1, 2)] * 2,
    "html": [htmltools.em("emphasized")] * 2,
    "html_str": [htmltools.HTML("<strong>bolded</strong>")] * 2,
    # "struct": [{"x": 1}, {"x": 2}],
}

ui.h2("data_frame column types")

with ui.card():
    ui.card_header("Pandas")

    @render.data_frame
    def pd_table():
        return render.DataGrid(pd.DataFrame(DATA), filters=True)


with ui.card():
    ui.card_header("Polars")

    @render.data_frame
    def pl_table():
        return render.DataGrid(pl.DataFrame(DATA), filters=True)
