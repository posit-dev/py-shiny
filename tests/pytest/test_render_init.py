"""Tests for shiny/render/__init__.py - Render module exports."""

from shiny import render


class TestRenderExports:
    """Tests for render module exports."""

    def test_data_frame_exported(self):
        """Test data_frame is exported."""
        assert hasattr(render, "data_frame")
        assert callable(render.data_frame)

    def test_express_exported(self):
        """Test express is exported."""
        assert hasattr(render, "express")
        assert callable(render.express)

    def test_text_exported(self):
        """Test text is exported."""
        assert hasattr(render, "text")
        assert callable(render.text)

    def test_code_exported(self):
        """Test code is exported."""
        assert hasattr(render, "code")
        assert callable(render.code)

    def test_plot_exported(self):
        """Test plot is exported."""
        assert hasattr(render, "plot")
        assert callable(render.plot)

    def test_image_exported(self):
        """Test image is exported."""
        assert hasattr(render, "image")
        assert callable(render.image)

    def test_table_exported(self):
        """Test table is exported."""
        assert hasattr(render, "table")
        assert callable(render.table)

    def test_ui_exported(self):
        """Test ui is exported."""
        assert hasattr(render, "ui")
        assert callable(render.ui)

    def test_download_exported(self):
        """Test download is exported."""
        assert hasattr(render, "download")
        assert callable(render.download)

    def test_datagrid_exported(self):
        """Test DataGrid is exported."""
        assert hasattr(render, "DataGrid")

    def test_datatable_exported(self):
        """Test DataTable is exported."""
        assert hasattr(render, "DataTable")

    def test_cellpatch_exported(self):
        """Test CellPatch is exported."""
        assert hasattr(render, "CellPatch")

    def test_cellvalue_exported(self):
        """Test CellValue is exported."""
        assert hasattr(render, "CellValue")

    def test_cellselection_exported(self):
        """Test CellSelection is exported."""
        assert hasattr(render, "CellSelection")

    def test_styleinfo_exported(self):
        """Test StyleInfo is exported."""
        assert hasattr(render, "StyleInfo")

    def test_transformer_submodule_exported(self):
        """Test transformer submodule is exported."""
        assert hasattr(render, "transformer")


class TestRenderAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(render.__all__, tuple)

    def test_all_contains_data_frame(self):
        """Test __all__ contains data_frame."""
        assert "data_frame" in render.__all__

    def test_all_contains_express(self):
        """Test __all__ contains express."""
        assert "express" in render.__all__

    def test_all_contains_text(self):
        """Test __all__ contains text."""
        assert "text" in render.__all__

    def test_all_contains_code(self):
        """Test __all__ contains code."""
        assert "code" in render.__all__

    def test_all_contains_plot(self):
        """Test __all__ contains plot."""
        assert "plot" in render.__all__

    def test_all_contains_image(self):
        """Test __all__ contains image."""
        assert "image" in render.__all__

    def test_all_contains_table(self):
        """Test __all__ contains table."""
        assert "table" in render.__all__

    def test_all_contains_ui(self):
        """Test __all__ contains ui."""
        assert "ui" in render.__all__

    def test_all_contains_download(self):
        """Test __all__ contains download."""
        assert "download" in render.__all__

    def test_all_contains_datagrid(self):
        """Test __all__ contains DataGrid."""
        assert "DataGrid" in render.__all__

    def test_all_contains_datatable(self):
        """Test __all__ contains DataTable."""
        assert "DataTable" in render.__all__

    def test_all_contains_cellpatch(self):
        """Test __all__ contains CellPatch."""
        assert "CellPatch" in render.__all__

    def test_all_contains_cellvalue(self):
        """Test __all__ contains CellValue."""
        assert "CellValue" in render.__all__

    def test_all_contains_cellselection(self):
        """Test __all__ contains CellSelection."""
        assert "CellSelection" in render.__all__

    def test_all_contains_styleinfo(self):
        """Test __all__ contains StyleInfo."""
        assert "StyleInfo" in render.__all__
