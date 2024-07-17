import pandas as pd
import pytest

from shiny import render
from shiny._deprecated import ShinyDeprecationWarning
from shiny.render._data_frame_utils._selection import SelectionModes


def test_data_frame_needs_unique_col_names():

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


def test_as_selection_modes_legacy():

    df = pd.DataFrame(data={"a": [1, 2]})

    with pytest.warns(ShinyDeprecationWarning, match="has been superseded"):
        dg = render.DataGrid(df, row_selection_mode="none")
    assert dg.selection_modes.row == SelectionModes(selection_mode_set={"none"}).row

    with pytest.warns(ShinyDeprecationWarning, match="has been superseded"):
        dg = render.DataGrid(df, row_selection_mode="single")
    assert dg.selection_modes.row == SelectionModes(selection_mode_set={"row"}).row

    with pytest.warns(ShinyDeprecationWarning, match="has been superseded"):
        dg = render.DataGrid(df, row_selection_mode="multiple")
    assert dg.selection_modes.row == SelectionModes(selection_mode_set={"rows"}).row

    with pytest.raises(ValueError, match="Unknown row_selection_mode: foo"):
        render.DataGrid(  # pyright: ignore[reportCallIssue]
            df,
            row_selection_mode="foo",  # pyright: ignore[reportArgumentType,reportGeneralTypeIssues]
        )


def test_as_selection_modes():
    with pytest.raises(ValueError) as e:
        SelectionModes(
            selection_mode_set={
                "foo",  # pyright: ignore[reportArgumentType,reportGeneralTypeIssues]
            }
        )
    assert "Unknown selection modes: foo" in str(e.value)

    with pytest.raises(
        ValueError, match="Cannot have other selection modes included with `none`"
    ):
        SelectionModes(selection_mode_set={"none", "row"})

    with pytest.raises(ValueError, match="Cannot have both `row` and `rows`"):
        SelectionModes(selection_mode_set={"row", "rows"})

    with pytest.raises(ValueError, match="Cannot have both `col` and `cols`"):
        SelectionModes(selection_mode_set={"col", "cols"})

    with pytest.raises(ValueError, match="Cannot have both `cell` and `region`"):
        SelectionModes(selection_mode_set={"cell", "region"})

    for sm in ("col", "cols", "cell", "region"):
        with pytest.raises(RuntimeError, match="based cell selections"):
            SelectionModes(selection_mode_set={sm})
