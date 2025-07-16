from typing import Any, cast

import pandas as pd
import pytest
from htmltools import TagChild, TagList

from shiny import reactive, render
from shiny._deprecated import ShinyDeprecationWarning
from shiny._namespaces import Root
from shiny._utils import wrap_async
from shiny.module import ResolvedId
from shiny.render._data_frame_utils._selection import SelectionModes
from shiny.render._data_frame_utils._tbl_data import as_data_frame
from shiny.session import Session, session_context
from shiny.session._session import RenderedDeps


class _MockSession:
    ns: ResolvedId = Root

    # Simplified version of `AppSession._process_ui()`
    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        res = TagList(ui).render()
        deps: list[dict[str, Any]] = []
        for dep in res["dependencies"]:
            # self.app._register_web_dependency(dep)
            dep_dict = dep.as_dict()
            deps.append(dep_dict)

        return {"deps": deps, "html": res["html"]}


test_session = cast(Session, _MockSession())


def test_data_frame_needs_unique_col_names():

    df = pd.DataFrame(data={"a": [1, 2]})
    df.insert(1, "a", [3, 4], True)  # pyright: ignore

    with pytest.raises(ValueError) as e:
        as_data_frame(df)
    assert "Expected unique column names" in str(e.value)


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


@pytest.mark.asyncio
async def test_as_data_frame_none():

    from typing import Any, Callable

    async def expect_data_is_not_none_error(fn: Callable[[], Any]):
        fn_async = wrap_async(fn)
        with pytest.raises(TypeError) as e:
            await fn_async()
        assert "`data` cannot be `None`" in str(e.value)

    @render.data_frame
    def pd_df():
        return pd.DataFrame(data={"a": [1, 2]})

    async def call_update_data():
        await pd_df.update_data(None)  # pyright: ignore[reportArgumentType]

    await expect_data_is_not_none_error(call_update_data)

    await expect_data_is_not_none_error(
        lambda: render.DataGrid(
            None  # pyright: ignore[reportArgumentType,reportUnknownLambdaType]
        )
    )
    await expect_data_is_not_none_error(
        lambda: render.DataTable(
            None  # pyright: ignore[reportArgumentType,reportUnknownLambdaType]
        )
    )


@pytest.mark.asyncio
async def test_update_cell_value_assertions():

    pd_data = pd.DataFrame(data={"a": [1, 2]})

    @render.data_frame
    def df():
        return pd_data

    with session_context(test_session):
        with reactive.isolate():
            df._value.set(render.DataGrid(pd_data))

            with pytest.raises(ValueError) as e:
                await df.update_cell_value("a", row=0, col="b")
            assert "Column 'b'" in str(e.value)

            with pytest.raises(TypeError) as e:
                await df.update_cell_value("a", row=0, col=True)
            assert "`col` to be an `int`" in str(e.value)

            with pytest.raises(ValueError) as e:
                await df.update_cell_value("a", row=0, col=-1)
            assert "`col` to be greater than" in str(e.value)
            with pytest.raises(ValueError) as e:
                await df.update_cell_value("a", row=0, col=10)
            assert "`col` to be less than" in str(e.value)

            with pytest.raises(TypeError) as e:
                await df.update_cell_value("a", row=True, col=0)
            assert "`row` to be an `int`" in str(e)
            with pytest.raises(ValueError) as e:
                await df.update_cell_value("a", row=-1, col=0)
            assert "`row` to be greater than" in str(e.value)
