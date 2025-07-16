from shared import mtcars

from shiny import reactive
from shiny.express import input, render, ui

data = reactive.value(mtcars.iloc[:, range(4)])

with ui.card():
    ui.input_action_button("btn", "Sort on columns 1↑ and 3↓")

    @render.data_frame
    def df():
        return render.DataGrid(data())


@reactive.effect
@reactive.event(input.btn)
async def _():
    await df.update_sort([{"col": 1, "desc": False}, {"col": 3, "desc": True}])
