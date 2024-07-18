from typing import cast

import pandas as pd
from palmerpenguins import load_penguins  # pyright: ignore[reportMissingTypeStubs]

from shiny import reactive
from shiny.express import input, render, ui

penguins = cast(pd.DataFrame, load_penguins())

ui.input_action_button("update_filters", "Update filters")
ui.input_action_button("reset_filters", "Reset filters")

ui.h5("Current filters: ", {"class": "pt-2"})


@render.code
def penguins_code():
    return str(penguins_df.filter())


@render.data_frame
def penguins_df():
    return render.DataGrid(penguins, filters=True)


@reactive.effect
@reactive.event(input.update_filters)
async def _():
    await penguins_df.update_filter(
        [
            {"col": 0, "value": "Gentoo"},
            {"col": 2, "value": (50, None)},
            {"col": 3, "value": (None, 17)},
            {"col": 4, "value": (220, 225)},
        ],
    )


@reactive.effect
@reactive.event(input.reset_filters)
async def _():
    await penguins_df.update_filter(None)  # <<
