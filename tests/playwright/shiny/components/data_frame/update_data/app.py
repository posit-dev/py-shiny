# TODO-barret; Test this app!

from __future__ import annotations

import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import pandas as pd

from shiny import reactive
from shiny.express import input, render, ui

pd_data = palmerpenguins.load_penguins_raw()


with ui.card():

    ui.input_action_button("shift_btn", "Shift data")
    ui.input_action_button("different_btn", "Change data set")

    ui.h4("Data")

    @render.data_frame
    def df():
        return render.DataGrid(
            pd_data.iloc[:, 0:2],
            selection_mode="rows",
            filters=True,
            editable=True,
        )

    ui.h4("Selected data")

    @render.data_frame
    def df_selected():
        return df.data_view(selected=True)


# Reactive value to store the un-subsetted data
full_data = reactive.value(pd_data)


@reactive.effect
@reactive.event(input.shift_btn)
async def shift_data():

    if not input.shift_btn():
        raise ValueError("update_btn must exist")

    k = 2
    shift = (k * input.shift_btn()) % full_data().shape[0]
    subsetted_data = full_data().iloc[(0 + shift) : (k + shift), 0:2]
    await df.update_data(subsetted_data)
    return


@reactive.effect
@reactive.event(input.different_btn)
async def different_data():

    if not input.different_btn():
        raise ValueError("different_btn must exist")

    print(
        "input.different_btn()", input.different_btn(), input.different_btn() % 2 == 0
    )
    if input.different_btn() % 2 == 0:
        await df.update_data(pd_data)
        full_data.set(pd_data)
        return

    new_df = pd.DataFrame(
        {
            "Letter": [
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
                "n",
                "o",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "v",
                "w",
                "x",
                "y",
                "z",
            ],
            "Negative index": [-1 * i for i in range(1, 27)],
        },
    )
    await df.update_data(new_df)
    full_data.set(new_df)
    return
