import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1")
    ),
    ui.input_select(
        "selection_mode",
        "Selection mode",
        {
            "none": "(None)",
            "row": "Single row",
            "rows": "Multiple rows",
        },
        selected="rows",
    ),
    ui.input_switch("filters", "Filters", True),
    ui.input_switch("editable", "Editable", True),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Data Frame as ", ui.tags.code("render.DataGrid")),
            ui.output_data_frame("grid"),
        ),
        ui.card(
            ui.card_header("Data Frame as ", ui.tags.code("render.DataTable")),
            ui.output_data_frame("table"),
        ),
        width=1 / 2,
    ),
    class_="p-3",
)


def server(input: Inputs, output: Outputs, session: Session):
    df: reactive.value[pd.DataFrame] = reactive.value(
        sns.load_dataset("anagrams").iloc[:, 1:]
    )

    def update_data_with_patch(patch):
        df_copy = df().copy()
        fn = str if patch["column_index"] == 0 else int
        df_copy.iat[patch["row_index"], patch["column_index"]] = fn(patch["value"])
        df.set(df_copy)

    height = 350
    width = "fit-content"

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


app = App(app_ui, server)
