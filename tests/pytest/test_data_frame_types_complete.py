"""Comprehensive tests for shiny.render._data_frame_utils._types module."""

from __future__ import annotations

from typing import Literal


class TestDataFrameTypes:
    """Tests for DataFrame and Series types."""

    def test_dataframe_import(self):
        """DataFrame should be importable."""
        from shiny.render._data_frame_utils._types import DataFrame

        assert DataFrame is not None

    def test_series_import(self):
        """Series should be importable."""
        from shiny.render._data_frame_utils._types import Series

        assert Series is not None


class TestPandasCompatible:
    """Tests for PandasCompatible protocol."""

    def test_pandas_compatible_protocol_exists(self):
        """PandasCompatible protocol should exist."""
        from shiny.render._data_frame_utils._types import PandasCompatible

        assert PandasCompatible is not None

    def test_pandas_compatible_is_runtime_checkable(self):
        """PandasCompatible should be runtime checkable."""
        from shiny.render._data_frame_utils._types import PandasCompatible

        # Should be able to check at runtime
        class FakePandasLike:
            def to_pandas(self):
                import pandas as pd

                return pd.DataFrame()

        obj = FakePandasLike()
        assert isinstance(obj, PandasCompatible)


class TestCellHtml:
    """Tests for CellHtml TypedDict."""

    def test_cell_html_structure(self):
        """CellHtml should have correct structure."""
        from shiny.render._data_frame_utils._types import CellHtml

        cell: CellHtml = {  # type: ignore[typeddict-item]
            "isShinyHtml": True,
            "obj": ([], {}),  # type: ignore
        }
        assert cell["isShinyHtml"] is True


class TestColumnSort:
    """Tests for ColumnSort TypedDict."""

    def test_column_sort_ascending(self):
        """ColumnSort should support ascending sort."""
        from shiny.render._data_frame_utils._types import ColumnSort

        sort: ColumnSort = {"col": 0, "desc": False}
        assert sort["col"] == 0
        assert sort["desc"] is False

    def test_column_sort_descending(self):
        """ColumnSort should support descending sort."""
        from shiny.render._data_frame_utils._types import ColumnSort

        sort: ColumnSort = {"col": 2, "desc": True}
        assert sort["col"] == 2
        assert sort["desc"] is True


class TestColumnFilterStr:
    """Tests for ColumnFilterStr TypedDict."""

    def test_column_filter_str_structure(self):
        """ColumnFilterStr should have correct structure."""
        from shiny.render._data_frame_utils._types import ColumnFilterStr

        filter_str: ColumnFilterStr = {"col": 1, "value": "test"}
        assert filter_str["col"] == 1
        assert filter_str["value"] == "test"


class TestColumnFilterNumber:
    """Tests for ColumnFilterNumber TypedDict."""

    def test_column_filter_number_range(self):
        """ColumnFilterNumber should support range values."""
        from shiny.render._data_frame_utils._types import ColumnFilterNumber

        filter_num: ColumnFilterNumber = {"col": 0, "value": (10, 20)}
        assert filter_num["col"] == 0
        assert filter_num["value"] == (10, 20)

    def test_column_filter_number_min_only(self):
        """ColumnFilterNumber should support min-only values."""
        from shiny.render._data_frame_utils._types import ColumnFilterNumber

        filter_num: ColumnFilterNumber = {"col": 1, "value": (5, None)}
        assert filter_num["value"][0] == 5
        assert filter_num["value"][1] is None

    def test_column_filter_number_max_only(self):
        """ColumnFilterNumber should support max-only values."""
        from shiny.render._data_frame_utils._types import ColumnFilterNumber

        filter_num: ColumnFilterNumber = {"col": 2, "value": (None, 100)}
        assert filter_num["value"][0] is None
        assert filter_num["value"][1] == 100


class TestDataViewInfo:
    """Tests for DataViewInfo TypedDict."""

    def test_data_view_info_structure(self):
        """DataViewInfo should have correct structure."""
        from shiny.render._data_frame_utils._types import DataViewInfo

        view: DataViewInfo = {
            "sort": ({"col": 0, "desc": False},),
            "filter": (),
            "rows": (0, 1, 2),
            "selected_rows": (0,),
        }
        assert len(view["sort"]) == 1
        assert len(view["filter"]) == 0
        assert len(view["rows"]) == 3
        assert len(view["selected_rows"]) == 1


class TestFrameRenderTypes:
    """Tests for FrameRender-related TypedDicts."""

    def test_frame_render_patch_info(self):
        """FrameRenderPatchInfo should have key field."""
        from shiny.render._data_frame_utils._types import FrameRenderPatchInfo

        patch: FrameRenderPatchInfo = {"key": "unique-key-123"}
        assert patch["key"] == "unique-key-123"

    def test_frame_render_selection_modes(self):
        """FrameRenderSelectionModes should have all mode fields."""
        from shiny.render._data_frame_utils._types import FrameRenderSelectionModes

        modes: FrameRenderSelectionModes = {
            "row": "single",
            "col": "multiple",
            "rect": "cell",
        }
        assert modes["row"] == "single"
        assert modes["col"] == "multiple"
        assert modes["rect"] == "cell"

    def test_frame_render_selection_modes_none_values(self):
        """FrameRenderSelectionModes should support 'none' values."""
        from shiny.render._data_frame_utils._types import FrameRenderSelectionModes

        modes: FrameRenderSelectionModes = {
            "row": "none",
            "col": "none",
            "rect": "none",
        }
        assert modes["row"] == "none"

    def test_frame_render_to_jsonifiable(self):
        """frame_render_to_jsonifiable should convert FrameRender."""
        from shiny.render._data_frame_utils._types import (
            FrameRender,
            frame_render_to_jsonifiable,
        )

        frame: FrameRender = {
            "payload": {
                "columns": ["A", "B"],
                "data": [[1, 2]],
                "typeHints": [{"type": "numeric"}, {"type": "numeric"}],
            },
            "patchInfo": {"key": "test"},
            "selectionModes": {"row": "single", "col": "none", "rect": "none"},
        }
        result = frame_render_to_jsonifiable(frame)
        assert "payload" in result
        assert "patchInfo" in result
        assert "selectionModes" in result


class TestFrameJsonTypes:
    """Tests for FrameJson and FrameJsonOptions."""

    def test_frame_json_options(self):
        """FrameJsonOptions should support all optional fields."""
        from shiny.render._data_frame_utils._types import FrameJsonOptions

        options: FrameJsonOptions = {
            "width": "100%",
            "height": 400,
            "summary": True,
            "filters": False,
            "editable": True,
            "style": "bootstrap",
            "fill": True,
        }
        assert options["width"] == "100%"
        assert options["height"] == 400
        assert options["summary"] is True

    def test_frame_json_minimal(self):
        """FrameJson should work with minimal required fields."""
        from shiny.render._data_frame_utils._types import FrameJson

        frame: FrameJson = {
            "columns": ["col1", "col2"],
            "data": [[1, 2], [3, 4]],
            "typeHints": [{"type": "numeric"}, {"type": "numeric"}],
        }
        assert len(frame["columns"]) == 2
        assert len(frame["data"]) == 2


class TestFrameDtypeTypes:
    """Tests for FrameDtype-related types."""

    def test_frame_dtype_subset_types(self):
        """FrameDtypeSubset should support all type literals."""
        from shiny.render._data_frame_utils._types import FrameDtypeSubset

        types_to_test: list[
            Literal[
                "string",
                "numeric",
                "boolean",
                "date",
                "datetime",
                "time",
                "duration",
                "object",
                "unknown",
                "html",
                "binary",
            ]
        ] = [
            "string",
            "numeric",
            "boolean",
            "date",
            "datetime",
            "time",
            "duration",
            "object",
            "unknown",
            "html",
            "binary",
        ]

        for dtype_type in types_to_test:
            dtype: FrameDtypeSubset = {"type": dtype_type}
            assert dtype["type"] == dtype_type

    def test_frame_dtype_categories(self):
        """FrameDtypeCategories should support categorical types."""
        from shiny.render._data_frame_utils._types import FrameDtypeCategories

        dtype: FrameDtypeCategories = {
            "type": "categorical",
            "categories": ["A", "B", "C"],
        }
        assert dtype["type"] == "categorical"
        assert len(dtype["categories"]) == 3


class TestStyleInfoTypes:
    """Tests for StyleInfo and BrowserStyleInfo."""

    def test_style_info_body_full(self):
        """StyleInfoBody should support all fields."""
        from shiny.render._data_frame_utils._types import StyleInfoBody

        style: StyleInfoBody = {
            "location": "body",
            "rows": [0, 1, 2],
            "cols": ["A", "B"],
            "style": {"background-color": "yellow"},
            "class": "highlight",
        }
        assert style["location"] == "body"
        assert style.get("class") == "highlight"

    def test_style_info_body_minimal(self):
        """StyleInfoBody should work with minimal fields."""
        from shiny.render._data_frame_utils._types import StyleInfoBody

        style: StyleInfoBody = {}
        # All fields are NotRequired
        assert isinstance(style, dict)

    def test_browser_style_info_body(self):
        """BrowserStyleInfoBody should require all fields."""
        from shiny.render._data_frame_utils._types import BrowserStyleInfoBody

        style: BrowserStyleInfoBody = {
            "location": "body",
            "rows": (0, 1, 2),
            "cols": (0, 1),
            "style": {"color": "red"},
            "class": "styled",
        }
        assert style["location"] == "body"
        assert isinstance(style["rows"], tuple)


class TestCellPatchTypes:
    """Tests for CellPatch and CellPatchProcessed."""

    def test_cell_patch_structure(self):
        """CellPatch should have correct structure."""
        from htmltools import Tag

        from shiny.render._data_frame_utils._types import CellPatch

        patch: CellPatch = {
            "row_index": 0,
            "column_index": 1,
            "value": Tag("div", "New value"),
        }
        assert patch["row_index"] == 0
        assert patch["column_index"] == 1

    def test_cell_patch_processed_structure(self):
        """CellPatchProcessed should have correct structure."""
        from shiny.render._data_frame_utils._types import CellPatchProcessed

        patch: CellPatchProcessed = {
            "row_index": 2,
            "column_index": 3,
            "value": "Updated text",
        }
        assert patch["row_index"] == 2
        assert patch["column_index"] == 3
        assert patch["value"] == "Updated text"

    def test_cell_patch_processed_to_jsonifiable(self):
        """cell_patch_processed_to_jsonifiable should convert patch."""
        from shiny.render._data_frame_utils._types import (
            CellPatchProcessed,
            cell_patch_processed_to_jsonifiable,
        )

        patch: CellPatchProcessed = {  # type: ignore[typeddict-item]
            "row_index": 0,
            "column_index": 0,
            "value": {"isShinyHtml": True, "obj": ([], {})},  # type: ignore
        }
        result = cell_patch_processed_to_jsonifiable(patch)
        assert "row_index" in result
        assert "column_index" in result
        assert "value" in result


class TestModuleExports:
    """Tests for module __all__ exports."""

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.render._data_frame_utils import _types

        for name in _types.__all__:
            assert hasattr(_types, name), f"{name} not found in module"

    def test_dtype_export(self):
        """DType should be exported."""
        from shiny.render._data_frame_utils._types import DType

        assert DType is not None

    def test_dataframe_t_export(self):
        """DataFrameT should be exported."""
        from shiny.render._data_frame_utils._types import DataFrameT

        assert DataFrameT is not None

    def test_into_dataframe_export(self):
        """IntoDataFrame should be exported."""
        from shiny.render._data_frame_utils._types import IntoDataFrame

        assert IntoDataFrame is not None

    def test_into_expr_export(self):
        """IntoExpr should be exported."""
        from shiny.render._data_frame_utils._types import IntoExpr

        assert IntoExpr is not None


class TestTypeAliases:
    """Tests for type aliases."""

    def test_rows_list_type(self):
        """RowsList type alias should work."""
        from shiny.render._data_frame_utils._types import RowsList

        rows: RowsList = [0, 1, 2]
        assert rows is not None

        rows_none: RowsList = None
        assert rows_none is None

    def test_cols_list_type(self):
        """ColsList type alias should work."""
        from shiny.render._data_frame_utils._types import ColsList

        cols: ColsList = ["A", "B", "C"]
        assert cols is not None

        cols_int: ColsList = [0, 1, 2]
        assert cols_int is not None

        cols_none: ColsList = None
        assert cols_none is None
