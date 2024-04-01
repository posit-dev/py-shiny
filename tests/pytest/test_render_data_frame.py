from pathlib import Path

import pandas as pd
import pytest

from shiny import render


def test_data_frame_needs_unique_col_names(tmp_path: Path):

    # TODO-barret; Add automated tests for this
    df = pd.DataFrame(data={"a": [1, 2]})
    df.insert(1, "a", [3, 4], True)  # pyright: ignore

    data_grid = render.DataGrid(df)
    data_table = render.DataTable(df)

    with pytest.raises(
        ValueError,
        match="column names of the pandas DataFrame are not unique",
    ):
        data_grid.to_payload()

    with pytest.raises(
        ValueError,
        match="column names of the pandas DataFrame are not unique",
    ):
        data_table.to_payload()
