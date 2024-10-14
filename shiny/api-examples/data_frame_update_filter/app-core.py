from shared import mtcars

from shiny import App, reactive, render, ui

app_ui = ui.page_fillable(
    ui.card(
        ui.layout_column_wrap(
            ui.input_action_button("btn", "Filter on columns 0, 1, and 3"),
            ui.input_action_button("reset", "Reset column filters"),
            fill=False,
        ),
        ui.output_data_frame("df"),
    ),
)


def server(input, output, session):
    data = reactive.value(mtcars.iloc[:, range(4)])

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


app = App(app_ui, server, debug=True)
