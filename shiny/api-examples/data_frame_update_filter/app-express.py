from shared import mtcars

from shiny import reactive
from shiny.express import input, render, ui

data = reactive.value(mtcars.iloc[:, range(4)])
with ui.card():
    with ui.layout_column_wrap(fill=False):
        ui.input_action_button("btn", "Filter on columns 0, 1, and 3")
        ui.input_action_button("reset", "Reset column filters")

    @render.data_frame
    def df():
        return render.DataGrid(data(), filters=True)


@reactive.effect
@reactive.event(input.reset)
async def _():
    await df.update_filter(None)


@reactive.effect
@reactive.event(input.btn)
async def _():
    await df.update_filter(
        [
            {"col": 0, "value": [19, 25]},
            {"col": 1, "value": [None, 6]},
            {"col": 3, "value": [100, None]},
        ]
    )
