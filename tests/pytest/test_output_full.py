"""Tests for shiny/ui/_output.py module."""

from shiny.ui._output import (
    output_image,
    output_plot,
    output_table,
    output_text,
    output_text_verbatim,
    output_ui,
)


class TestOutputUi:
    """Tests for output_ui function."""

    def test_output_ui_is_callable(self):
        """Test output_ui is callable."""
        assert callable(output_ui)

    def test_output_ui_returns_tag(self):
        """Test output_ui returns a Tag."""
        from htmltools import Tag

        result = output_ui("my_output")
        assert isinstance(result, Tag)


class TestOutputText:
    """Tests for output_text function."""

    def test_output_text_is_callable(self):
        """Test output_text is callable."""
        assert callable(output_text)

    def test_output_text_returns_tag(self):
        """Test output_text returns a Tag."""
        from htmltools import Tag

        result = output_text("my_text")
        assert isinstance(result, Tag)


class TestOutputTextVerbatim:
    """Tests for output_text_verbatim function."""

    def test_output_text_verbatim_is_callable(self):
        """Test output_text_verbatim is callable."""
        assert callable(output_text_verbatim)

    def test_output_text_verbatim_returns_tag(self):
        """Test output_text_verbatim returns a Tag."""
        from htmltools import Tag

        result = output_text_verbatim("my_verbatim")
        assert isinstance(result, Tag)


class TestOutputImage:
    """Tests for output_image function."""

    def test_output_image_is_callable(self):
        """Test output_image is callable."""
        assert callable(output_image)

    def test_output_image_returns_tag(self):
        """Test output_image returns a Tag."""
        from htmltools import Tag

        result = output_image("my_image")
        assert isinstance(result, Tag)


class TestOutputPlot:
    """Tests for output_plot function."""

    def test_output_plot_is_callable(self):
        """Test output_plot is callable."""
        assert callable(output_plot)

    def test_output_plot_returns_tag(self):
        """Test output_plot returns a Tag."""
        from htmltools import Tag

        result = output_plot("my_plot")
        assert isinstance(result, Tag)


class TestOutputTable:
    """Tests for output_table function."""

    def test_output_table_is_callable(self):
        """Test output_table is callable."""
        assert callable(output_table)

    def test_output_table_returns_tag(self):
        """Test output_table returns a Tag."""
        from htmltools import Tag

        result = output_table("my_table")
        assert isinstance(result, Tag)


class TestOutputExported:
    """Tests for output functions export."""

    def test_output_ui_in_ui(self):
        """Test output_ui is in ui module."""
        from shiny import ui

        assert hasattr(ui, "output_ui")

    def test_output_text_in_ui(self):
        """Test output_text is in ui module."""
        from shiny import ui

        assert hasattr(ui, "output_text")

    def test_output_plot_in_ui(self):
        """Test output_plot is in ui module."""
        from shiny import ui

        assert hasattr(ui, "output_plot")

    def test_output_image_in_ui(self):
        """Test output_image is in ui module."""
        from shiny import ui

        assert hasattr(ui, "output_image")

    def test_output_table_in_ui(self):
        """Test output_table is in ui module."""
        from shiny import ui

        assert hasattr(ui, "output_table")
