# TODO-barret; Test this app!

from __future__ import annotations

import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import pandas as pd

from shiny import reactive
from shiny.express import input, render, ui

pd_df = palmerpenguins.load_penguins_raw()


with ui.card():

    ui.input_action_button("shift_btn", "Shift data")
    ui.input_action_button("different_btn", "Change data set")

    ui.h4("Data")

    @render.data_frame
    def dt():
        return render.DataGrid(
            pd_df.iloc[:, 0:2],
            selection_mode="rows",
            filters=True,
            editable=True,
        )

    ui.h4("Selected data")

    @render.data_frame
    def dt_selected():
        return dt.data_view(selected=True)

    @reactive.effect
    @reactive.event(dt.cell_selection)
    def _on_cell_selection():
        print("Cell selected", dt.cell_selection())
        return


data_val = reactive.value(pd_df)


@reactive.effect
@reactive.event(input.shift_btn)
async def shift_data():

    if not input.shift_btn():
        raise ValueError("update_btn must exist")

    k = 2
    shift = (k * input.shift_btn()) % data_val().shape[0]
    await dt.update_data(data_val().iloc[(0 + shift) : (k + shift), 0:2])
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
        # await dt.update_data(pd_df.iloc[:, 0:2])
        await dt.update_data(pd_df)
        data_val.set(pd_df)
        return

    new_df = pd.DataFrame(
        {
            "studyName": [
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
            "Sample Number": [-1 * i for i in range(1, 27)],
        },
    )
    await dt.update_data(new_df)
    data_val.set(new_df)
    return
