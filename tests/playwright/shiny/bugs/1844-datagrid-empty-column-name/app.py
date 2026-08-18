import pandas as pd

from shiny import App, Inputs, reactive, render, ui

# The empty column name sits at index 0 in `df_first` and at index 1 in
# `df_mid`, so the client's column id <-> column index translation is exercised
# at more than one position. The empty column holds the same values in both, so
# both grids sort and filter to the same row order.
df_first = pd.DataFrame({"": ["c", "a", "b"], "num": [3, 1, 2]})
df_mid = pd.DataFrame({"chr": ["x", "y", "z"], "": ["c", "a", "b"], "num": [3, 1, 2]})

# pandas allows non-string column names, and they reach the client as raw JSON
# numbers. Column ids must not be derived from them either. `0` is the value
# that a falsy check mistakes for "no name".
#
# NOTE: pandas unifies the column index dtype, so adding `1.5` to this frame
# would silently retype `0` and `1` as `0.0` and `1.0` and stop covering
# integer names at all. The non-integer name needs its own frame.
df_int_names = pd.DataFrame({0: ["c", "a", "b"], 1: [3, 1, 2]})
df_float_names = pd.DataFrame({1.5: ["c", "a", "b"], 2.5: [3, 1, 2]})

app_ui = ui.page_fluid(
    ui.input_action_button("update_sort", "Update sort"),
    ui.input_action_button("update_sort_int", "Update sort (bare index)"),
    ui.input_action_button("update_filter", "Update filter"),
    ui.output_data_frame("df1"),
    ui.output_code("sort_value", placeholder=True),
    ui.output_code("filter_value", placeholder=True),
    ui.output_code("data_view_rows", placeholder=True),
    ui.output_data_frame("df2"),
    ui.output_code("sort_value2", placeholder=True),
    ui.output_code("filter_value2", placeholder=True),
    ui.output_code("data_view_rows2", placeholder=True),
    ui.output_data_frame("df3"),
    ui.output_code("sort_value3", placeholder=True),
    ui.output_code("data_view_rows3", placeholder=True),
    ui.output_data_frame("df4"),
    ui.output_code("sort_value4", placeholder=True),
)


def server(input: Inputs):
    @render.data_frame
    def df1():
        return render.DataGrid(df_first, filters=True)

    @render.data_frame
    def df2():
        return render.DataGrid(df_mid, filters=True)

    @render.data_frame
    def df3():
        return render.DataGrid(df_int_names)

    @render.data_frame
    def df4():
        return render.DataGrid(df_float_names)

    @render.code
    def sort_value():
        return f"sort: {df1.sort()}"

    @render.code
    def filter_value():
        return f"filter: {df1.filter()}"

    @render.code
    def data_view_rows():
        return f"rows: {df1.data_view_rows()}"

    @render.code
    def sort_value2():
        return f"sort: {df2.sort()}"

    @render.code
    def filter_value2():
        return f"filter: {df2.filter()}"

    @render.code
    def data_view_rows2():
        return f"rows: {df2.data_view_rows()}"

    @render.code
    def sort_value3():
        return f"sort: {df3.sort()}"

    @render.code
    def data_view_rows3():
        return f"rows: {df3.data_view_rows()}"

    @render.code
    def sort_value4():
        return f"sort: {df4.sort()}"

    @reactive.effect
    @reactive.event(input.update_sort)
    async def _():
        await df1.update_sort([{"col": 0, "desc": True}])
        await df2.update_sort([{"col": 1, "desc": True}])

    @reactive.effect
    @reactive.event(input.update_sort_int)
    async def _():
        # A bare column index derives `desc` from the column dtype: the
        # empty-named column is string-like (ascending) and `num` is number-like
        # (descending).
        await df1.update_sort(0)
        await df2.update_sort(2)

    @reactive.effect
    @reactive.event(input.update_filter)
    async def _():
        await df1.update_filter([{"col": 0, "value": "b"}])
        await df2.update_filter([{"col": 1, "value": "b"}])


app = App(app_ui, server)
