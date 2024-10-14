from __future__ import annotations

import pkgutil

import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import polars as pl
from narwhals.stable.v1.typing import IntoDataFrame

from shiny import Inputs, Outputs, Session
from shiny.express import module, render, ui

pd_penguins = palmerpenguins.load_penguins_raw()[["Sample Number", "Species", "Region"]]
pl_penguins = pl.read_csv(
    pkgutil.get_data(  # pyright: ignore[reportArgumentType]
        "palmerpenguins", "data/penguins-raw.csv"
    )
)[["Sample Number", "Species", "Region"]]


@module
def df_mod(
    input: Inputs,
    output: Outputs,
    session: Session,
    name: str,
    data: IntoDataFrame,
):

    ui.hr()

    ui.h1(f"{name}")

    ui.h2("Column labels w/ and w/o filters")

    ui.h3("With filters")

    @render.data_frame
    def w_filters():
        return render.DataGrid(data, filters=True)

    ui.h3("Without filters")

    @render.data_frame
    def wo_filters():
        return render.DataGrid(data, filters=False)


df_mod("pandas", "pandas", pd_penguins)
df_mod("polars", "polars", pl_penguins)
