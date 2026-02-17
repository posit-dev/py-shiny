"""Tests for shiny/render/_data_frame_utils/_types.py"""

from __future__ import annotations

from typing import Any, Literal

from shiny.render._data_frame_utils._types import (
    BrowserStyleInfoBody,
    CellPatch,
    CellPatchProcessed,
    ColumnFilterNumber,
    ColumnFilterStr,
    ColumnSort,
    DataViewInfo,
    FrameDtypeCategories,
    FrameDtypeSubset,
    FrameJsonOptions,
    FrameRender,
    FrameRenderPatchInfo,
    FrameRenderSelectionModes,
    PandasCompatible,
    StyleInfoBody,
    cell_patch_processed_to_jsonifiable,
    frame_render_to_jsonifiable,
)


class TestPandasCompatible:
    """Tests for the PandasCompatible protocol."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """Test that PandasCompatible can be used with isinstance."""

        class HasToPandas:
            def to_pandas(self) -> Any:
                return None

        class NoToPandas:
            pass

        assert isinstance(HasToPandas(), PandasCompatible)
        assert not isinstance(NoToPandas(), PandasCompatible)
        assert not isinstance("string", PandasCompatible)
        assert not isinstance(123, PandasCompatible)


class TestColumnSort:
    """Tests for the ColumnSort TypedDict."""

    def test_column_sort_creation(self) -> None:
        """Test creating a ColumnSort."""
        sort: ColumnSort = {"col": 0, "desc": True}
        assert sort["col"] == 0
        assert sort["desc"] is True

    def test_column_sort_ascending(self) -> None:
        """Test ColumnSort with ascending order."""
        sort: ColumnSort = {"col": 5, "desc": False}
        assert sort["col"] == 5
        assert sort["desc"] is False


class TestColumnFilterStr:
    """Tests for the ColumnFilterStr TypedDict."""

    def test_column_filter_str_creation(self) -> None:
        """Test creating a ColumnFilterStr."""
        filter_str: ColumnFilterStr = {"col": 2, "value": "test"}
        assert filter_str["col"] == 2
        assert filter_str["value"] == "test"


class TestColumnFilterNumber:
    """Tests for the ColumnFilterNumber TypedDict."""

    def test_column_filter_number_range(self) -> None:
        """Test ColumnFilterNumber with a range."""
        filter_num: ColumnFilterNumber = {"col": 1, "value": (10, 20)}
        assert filter_num["col"] == 1
        assert filter_num["value"] == (10, 20)

    def test_column_filter_number_min_only(self) -> None:
        """Test ColumnFilterNumber with min only."""
        filter_num: ColumnFilterNumber = {"col": 1, "value": (10, None)}
        assert filter_num["value"] == (10, None)

    def test_column_filter_number_max_only(self) -> None:
        """Test ColumnFilterNumber with max only."""
        filter_num: ColumnFilterNumber = {"col": 1, "value": (None, 20)}
        assert filter_num["value"] == (None, 20)


class TestDataViewInfo:
    """Tests for the DataViewInfo TypedDict."""

    def test_data_view_info_creation(self) -> None:
        """Test creating a DataViewInfo."""
        info: DataViewInfo = {
            "sort": ({"col": 0, "desc": True},),
            "filter": ({"col": 1, "value": "test"},),
            "rows": (0, 1, 2),
            "selected_rows": (1,),
        }
        assert len(info["sort"]) == 1
        assert len(info["filter"]) == 1
        assert info["rows"] == (0, 1, 2)
        assert info["selected_rows"] == (1,)


class TestFrameRenderPatchInfo:
    """Tests for the FrameRenderPatchInfo TypedDict."""

    def test_frame_render_patch_info_creation(self) -> None:
        """Test creating a FrameRenderPatchInfo."""
        patch_info: FrameRenderPatchInfo = {"key": "unique_key"}
        assert patch_info["key"] == "unique_key"


class TestFrameRenderSelectionModes:
    """Tests for the FrameRenderSelectionModes TypedDict."""

    def test_frame_render_selection_modes_creation(self) -> None:
        """Test creating a FrameRenderSelectionModes."""
        modes: FrameRenderSelectionModes = {
            "row": "multiple",
            "col": "single",
            "rect": "cell",
        }
        assert modes["row"] == "multiple"
        assert modes["col"] == "single"
        assert modes["rect"] == "cell"


class TestFrameRenderToJsonifiable:
    """Tests for the frame_render_to_jsonifiable function."""

    def test_frame_render_to_jsonifiable(self) -> None:
        """Test converting FrameRender to jsonifiable dict."""
        frame_render: FrameRender = {
            "payload": {
                "columns": ["a", "b"],
                "data": [[1, 2], [3, 4]],
                "typeHints": [{"type": "numeric"}, {"type": "numeric"}],
            },
            "patchInfo": {"key": "test_key"},
            "selectionModes": {"row": "none", "col": "none", "rect": "none"},
        }
        result = frame_render_to_jsonifiable(frame_render)
        assert isinstance(result, dict)
        assert "payload" in result
        assert "patchInfo" in result
        assert "selectionModes" in result


class TestFrameJsonOptions:
    """Tests for the FrameJsonOptions TypedDict."""

    def test_frame_json_options_creation(self) -> None:
        """Test creating a FrameJsonOptions."""
        options: FrameJsonOptions = {
            "width": "100%",
            "height": "400px",
            "summary": True,
            "filters": True,
            "editable": False,
            "style": "grid",
            "fill": True,
        }
        assert options["width"] == "100%"
        assert options["editable"] is False


class TestFrameDtypeSubset:
    """Tests for the FrameDtypeSubset TypedDict."""

    def test_frame_dtype_subset_string(self) -> None:
        """Test FrameDtypeSubset with string type."""
        dtype: FrameDtypeSubset = {"type": "string"}
        assert dtype["type"] == "string"

    def test_frame_dtype_subset_numeric(self) -> None:
        """Test FrameDtypeSubset with numeric type."""
        dtype: FrameDtypeSubset = {"type": "numeric"}
        assert dtype["type"] == "numeric"

    def test_frame_dtype_subset_all_types(self) -> None:
        """Test all FrameDtypeSubset types."""
        types: list[
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
        for t in types:
            dtype: FrameDtypeSubset = {"type": t}
            assert dtype["type"] == t


class TestFrameDtypeCategories:
    """Tests for the FrameDtypeCategories TypedDict."""

    def test_frame_dtype_categories_creation(self) -> None:
        """Test creating a FrameDtypeCategories."""
        dtype: FrameDtypeCategories = {
            "type": "categorical",
            "categories": ["a", "b", "c"],
        }
        assert dtype["type"] == "categorical"
        assert dtype["categories"] == ["a", "b", "c"]


class TestStyleInfoBody:
    """Tests for the StyleInfoBody TypedDict."""

    def test_style_info_body_creation(self) -> None:
        """Test creating a StyleInfoBody."""
        style: StyleInfoBody = {
            "location": "body",
            "rows": [0, 1, 2],
            "cols": ["a", "b"],
            "style": {"color": "red"},
            "class": "highlight",
        }
        assert style["location"] == "body"
        assert style["rows"] == [0, 1, 2]
        assert style["class"] == "highlight"

    def test_style_info_body_minimal(self) -> None:
        """Test StyleInfoBody with minimal fields."""
        style: StyleInfoBody = {}
        assert isinstance(style, dict)


class TestBrowserStyleInfoBody:
    """Tests for the BrowserStyleInfoBody TypedDict."""

    def test_browser_style_info_body_creation(self) -> None:
        """Test creating a BrowserStyleInfoBody."""
        style: BrowserStyleInfoBody = {
            "location": "body",
            "rows": (0, 1, 2),
            "cols": (0, 1),
            "style": {"background": "blue"},
            "class": "selected",
        }
        assert style["location"] == "body"
        assert style["rows"] == (0, 1, 2)
        assert style["cols"] == (0, 1)


class TestCellPatch:
    """Tests for the CellPatch TypedDict."""

    def test_cell_patch_creation(self) -> None:
        """Test creating a CellPatch."""
        patch: CellPatch = {
            "row_index": 5,
            "column_index": 3,
            "value": "new_value",
        }
        assert patch["row_index"] == 5
        assert patch["column_index"] == 3
        assert patch["value"] == "new_value"


class TestCellPatchProcessed:
    """Tests for the CellPatchProcessed TypedDict."""

    def test_cell_patch_processed_string_value(self) -> None:
        """Test CellPatchProcessed with string value."""
        patch: CellPatchProcessed = {
            "row_index": 1,
            "column_index": 2,
            "value": "processed_value",
        }
        assert patch["value"] == "processed_value"


class TestCellPatchProcessedToJsonifiable:
    """Tests for the cell_patch_processed_to_jsonifiable function."""

    def test_cell_patch_processed_to_jsonifiable(self) -> None:
        """Test converting CellPatchProcessed to jsonifiable dict."""
        patch: CellPatchProcessed = {
            "row_index": 0,
            "column_index": 0,
            "value": "test",
        }
        result = cell_patch_processed_to_jsonifiable(patch)
        assert isinstance(result, dict)
        assert result["row_index"] == 0
        assert result["column_index"] == 0
        assert result["value"] == "test"
