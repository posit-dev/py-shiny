from __future__ import annotations

import pandas as pd

from shiny.express import render, ui

df = pd.DataFrame(
    {
        "a": [1, 2, 3],
        "b": [4, 5, 6],
        "c": [7, 8, 9],
    }
)

ui.markdown(
    """
    * Edit a cell in column `b`.
    * Column `a` should be updated to `a value`
    * The edited cell should be back to a `ready` state
    """
)


@render.data_frame
def my_df():
    return render.DataTable(
        df,
        editable=True,
    )


# just testing if it works when editing another cell
@my_df.set_patches_fn
def edt(*, patches: tuple[render.CellPatch, ...]) -> list[render.CellPatch]:
    patch = patches[0]
    return [
        render.CellPatch(
            {
                "row_index": patch["row_index"],
                "column_index": 0,
                "value": "a value",
            },
        ),
    ]
