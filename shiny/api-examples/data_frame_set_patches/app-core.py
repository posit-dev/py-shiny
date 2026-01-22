from __future__ import annotations

from pathlib import Path

import pandas as pd

from shiny import App, reactive, render, ui

app_ui = ui.page_fillable(
    {"class": "p-3"},
    ui.markdown(
        """
        #### Instructions:
        * Run the app locally so that the edits to the underlying CSV file will persist.
        * Edit the cells in the table.

        #### Note:
        The data frame will not be re-rendered as the result of `df()` has not updated.

        Once the `df()` is invalidated, all local edits are forgotten, and the data frame will be re-rendered. However, since the edits were saved to the CSV file, the edits will persist between refreshes (when run locally).
        """
    ),
    ui.card(
        ui.output_data_frame("my_data_frame"),
    ),
)

here = Path(__file__).parent


def server(input, output, session):
    mtcars_df = reactive.value(pd.read_csv(here / "mtcars.csv").iloc[:, range(4)])

    # A copy of the data frame that will store all the edits
    edited_df = reactive.value(None)

    # Copy mtcars_df to edited_df when mtcars_df changes and on initial load
    @reactive.effect
    def _sync_mtcars_to_edited_df():
        edited_df.set(mtcars_df())

    @render.data_frame
    def my_data_frame():
        return render.DataGrid(
            mtcars_df(),
            editable=True,
        )

    # Save the edited values to the data source (ex: the CSV file)
    @my_data_frame.set_patches_fn
    def _(*, patches: list[render.CellPatch]) -> list[render.CellPatch]:
        for patch in patches:
            if patch["column_index"] in [0, 2]:
                patch["value"] = float(patch["value"])
            else:
                patch["value"] = int(patch["value"])

        # "Save to the database" by writing the edited data to a CSV file
        df = edited_df().copy()
        for patch in patches:
            df.iloc[patch["row_index"], patch["column_index"]] = patch["value"]
        edited_df.set(df)
        df.to_csv(here / "mtcars.csv", index=False)
        print("Saved the edited data to './mtcars.csv'")

        return patches


app = App(app_ui, server)
