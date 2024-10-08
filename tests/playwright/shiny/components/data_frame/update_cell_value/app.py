# TODO-barret; Test this app!

from __future__ import annotations

import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import polars as pl

from shiny import reactive
from shiny.express import input, render, ui

pd_data = palmerpenguins.load_penguins_raw().iloc[0:2, 0:2]
pl_data = pl.DataFrame(pd_data)

with ui.layout_column_wrap(width=1 / 2):

    with ui.card():

        ui.h3("Pandas")

        ui.input_action_button("update_pd_btn", "Update cell")

        @render.data_frame
        def pd_df():
            return pd_data

    @reactive.effect
    @reactive.event(input.update_pd_btn)
    async def _():

        await pd_df.update_cell_value(
            "pandas - " + str(input.update_pd_btn()),
            row=0,
            col=0,
        )

    with ui.card():

        ui.h3("Polars")
        ui.input_action_button("update_pl_btn", "Update cell")

        @render.data_frame
        def pl_df():
            return pl_data

    @reactive.effect
    @reactive.event(input.update_pl_btn)
    async def _():

        await pl_df.update_cell_value(
            "polars - " + str(input.update_pl_btn()),
            row=0,
            col=0,
        )
