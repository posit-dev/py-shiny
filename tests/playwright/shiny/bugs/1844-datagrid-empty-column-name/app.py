import pandas as pd

from shiny import App, Inputs, reactive, render, ui

df = pd.DataFrame({"": ["c", "a", "b"], "num": [3, 1, 2]})

app_ui = ui.page_fluid(
    ui.input_action_button("update_sort", "Update sort"),
    ui.input_action_button("update_filter", "Update filter"),
    ui.output_data_frame("df1"),
    ui.output_code("sort_value", placeholder=True),
    ui.output_code("filter_value", placeholder=True),
    ui.output_code("data_view_rows", placeholder=True),
)


def server(input: Inputs):
    @render.data_frame
    def df1():
        return render.DataGrid(df, filters=True)

    @render.code
    def sort_value():
        return f"sort: {df1.sort()}"

    @render.code
    def filter_value():
        return f"filter: {df1.filter()}"

    @render.code
    def data_view_rows():
        return f"rows: {df1.data_view_rows()}"

    @reactive.effect
    @reactive.event(input.update_sort)
    async def _():
        await df1.update_sort([{"col": 0, "desc": True}])

    @reactive.effect
    @reactive.event(input.update_filter)
    async def _():
        await df1.update_filter([{"col": 0, "value": "b"}])


app = App(app_ui, server)
