from __future__ import annotations

import narwhals.stable.v1 as nw
import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]

from shiny import reactive
from shiny.express import input, render, ui

pd_df = palmerpenguins.load_penguins_raw().iloc[0:2, 0:2]

with ui.card():

    ui.input_action_button("update_btn", "Update cell")

    @render.data_frame
    def dt():
        return pd_df


@reactive.effect
@reactive.event(input.update_btn)
async def update_cell():

    await dt.update_cell_value(
        "new_value - " + str(input.update_btn()),
        row=0,
        col=0,
    )
