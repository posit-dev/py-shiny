from __future__ import annotations

import narwhals.stable.v1 as nw
import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]

from shiny.express import render, ui

pd_df = palmerpenguins.load_penguins_raw().iloc[0:2, 0:2]

nw_df = nw.from_native(pd_df, eager_only=True)

with ui.card():

    ui.h2("Polars Pandas Data")

    @render.table
    def nw_table():
        return nw_df

    "Data type:"

    @render.code
    def pd_type():
        return str(type(nw_df))
