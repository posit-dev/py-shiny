from __future__ import annotations

import modin.pandas as md  # pyright: ignore[reportMissingTypeStubs]
import narwhals.stable.v1 as nw
import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]

from shiny.express import render, ui

pd_df = palmerpenguins.load_penguins_raw().iloc[0:2, 0:2]

nw_df = nw.from_native(pd_df, eager_only=True)

md_df = md.DataFrame(pd_df)

with ui.card():

    ui.h2("Polars Pandas Data")

    @render.table
    def nw_table():
        return nw_df

    "Data type:"

    @render.code
    def nw_df_type():
        return str(type(nw_df))


with ui.card():

    ui.h2("Modin dataframe Data")

    @render.table
    def md_table():
        return md_df

    "Data type:"

    @render.code
    def md_df_type():
        return str(type(md_df))
