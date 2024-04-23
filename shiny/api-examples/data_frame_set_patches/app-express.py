from __future__ import annotations

from pathlib import Path

import pandas as pd

from shiny import reactive
from shiny.express import render, ui

here = Path(__file__).parent
mtcars_df = reactive.value(pd.read_csv(here / "mtcars.csv").iloc[:, range(4)])


ui.markdown(
    """
    #### Instructions:
    * Run the app locally so that the edits to the underlying CSV file will persist.
    * Edit the cells in the table.

    #### Note:
    The data frame will not be re-rendered as the result of `df()` has not updated.

    Once the `df()` is invalidated, all local edits are forgotten, and the data frame will be re-rendered. However, since the edits were saved to the CSV file, the edits will persist between refreshes (when run locally).
    """
)

with ui.card():

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
        for patch in patches:
            df = mtcars_df().copy()
            df.iloc[patch["row_index"], patch["column_index"]] = patch["value"]
        df.to_csv(here / "mtcars.csv", index=False)
        print("Saved the edited data to './mtcars.csv'")

        return patches
