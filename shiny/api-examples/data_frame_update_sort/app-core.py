from shared import mtcars

from shiny import App, reactive, render, ui

app_ui = ui.page_fillable(
    ui.card(
        ui.layout_column_wrap(
            ui.input_action_button("btn", "Sort on columns 1↑ and 3↓"),
            ui.input_action_button("reset", "Reset sorting"),
            fill=False,
        ),
        ui.output_data_frame("df"),
    ),
)


def server(input, output, session):
    data = reactive.value(mtcars.iloc[:, range(4)])

    @render.data_frame
    def df():
        return render.DataGrid(data())

    @reactive.effect
    @reactive.event(input.reset)
    async def _():
        await df.update_sort(None)

    @reactive.effect
    @reactive.event(input.btn)
    async def _():
        await df.update_sort([{"col": 1, "desc": False}, {"col": 3, "desc": True}])


app = App(app_ui, server, debug=True)
