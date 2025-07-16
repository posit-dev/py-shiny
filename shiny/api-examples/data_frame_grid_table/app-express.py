import pandas as pd
import seaborn as sns

from shiny import reactive
from shiny.express import input, render, ui

height = 350
width = "fit-content"
df: reactive.value[pd.DataFrame] = reactive.value(
    sns.load_dataset("anagrams").iloc[:, 1:]
)


def update_data_with_patch(patch):
    df_copy = df().copy()
    fn = str if patch["column_index"] == 0 else int
    df_copy.iat[patch["row_index"], patch["column_index"]] = fn(patch["value"])
    df.set(df_copy)


ui.head_content(
    ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1")
)
ui.input_select(
    "selection_mode",
    "Selection mode",
    {
        "none": "(None)",
        "row": "Single row",
        "rows": "Multiple rows",
    },
    selected="rows",
)
ui.input_switch("filters", "Filters", True)
ui.input_switch("editable", "Editable", True)

with ui.layout_column_wrap(width=1 / 2):
    with ui.card():
        ui.card_header("Data Frame as ", ui.tags.code("render.DataGrid"))

        @render.data_frame
        def grid():
            return render.DataGrid(
                df(),
                width=width,
                height=height,
                filters=input.filters(),
                editable=input.editable(),
                selection_mode=input.selection_mode(),
            )

        @grid.set_patch_fn
        def _(*, patch: render.CellPatch):
            update_data_with_patch(patch)
            return patch["value"]

    with ui.card():
        ui.card_header("Data Frame as ", ui.tags.code("render.DataTable"))

        @render.data_frame
        def table():
            return render.DataTable(
                df(),
                width=width,
                height=height,
                filters=input.filters(),
                editable=input.editable(),
                selection_mode=input.selection_mode(),
            )

        @table.set_patch_fn
        def _(*, patch: render.CellPatch):
            update_data_with_patch(patch)
            return patch["value"]
