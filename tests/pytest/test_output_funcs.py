"""Tests for shiny.ui._output module."""

from htmltools import Tag

from shiny.ui._output import (
    output_image,
    output_plot,
    output_table,
    output_text,
    output_text_verbatim,
    output_ui,
)


class TestOutputText:
    """Tests for output_text function."""

    def test_output_text_basic(self) -> None:
        """Test basic output_text creation."""
        result = output_text("my_text")
        assert isinstance(result, Tag)

    def test_output_text_has_id(self) -> None:
        """Test output_text has correct id."""
        result = output_text("my_text_output")
        html = str(result)
        assert "my_text_output" in html

    def test_output_text_inline_true(self) -> None:
        """Test output_text with inline=True."""
        result = output_text("text_output", inline=True)
        html = str(result)
        # inline outputs use span instead of div
        assert "<span" in html

    def test_output_text_inline_false(self) -> None:
        """Test output_text with inline=False."""
        result = output_text("text_output", inline=False)
        html = str(result)
        assert "<div" in html


class TestOutputTextVerbatim:
    """Tests for output_text_verbatim function."""

    def test_output_text_verbatim_basic(self) -> None:
        """Test basic output_text_verbatim creation."""
        result = output_text_verbatim("verbatim_output")
        assert isinstance(result, Tag)

    def test_output_text_verbatim_has_id(self) -> None:
        """Test output_text_verbatim has correct id."""
        result = output_text_verbatim("my_verbatim")
        html = str(result)
        assert "my_verbatim" in html

    def test_output_text_verbatim_pre_tag(self) -> None:
        """Test output_text_verbatim uses pre tag."""
        result = output_text_verbatim("verbatim_output")
        html = str(result)
        assert "<pre" in html

    def test_output_text_verbatim_placeholder(self) -> None:
        """Test output_text_verbatim with placeholder."""
        result = output_text_verbatim("verbatim", placeholder=True)
        html = str(result)
        assert "verbatim" in html


class TestOutputUI:
    """Tests for output_ui function."""

    def test_output_ui_basic(self) -> None:
        """Test basic output_ui creation."""
        result = output_ui("my_ui")
        assert isinstance(result, Tag)

    def test_output_ui_has_id(self) -> None:
        """Test output_ui has correct id."""
        result = output_ui("ui_output")
        html = str(result)
        assert "ui_output" in html

    def test_output_ui_inline_true(self) -> None:
        """Test output_ui with inline=True."""
        result = output_ui("ui_output", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_ui_inline_false(self) -> None:
        """Test output_ui with inline=False."""
        result = output_ui("ui_output", inline=False)
        html = str(result)
        assert "<div" in html


class TestOutputPlot:
    """Tests for output_plot function."""

    def test_output_plot_basic(self) -> None:
        """Test basic output_plot creation."""
        result = output_plot("my_plot")
        assert isinstance(result, Tag)

    def test_output_plot_has_id(self) -> None:
        """Test output_plot has correct id."""
        result = output_plot("plot_output")
        html = str(result)
        assert "plot_output" in html

    def test_output_plot_with_width(self) -> None:
        """Test output_plot with width parameter."""
        result = output_plot("plot", width="400px")
        html = str(result)
        assert "plot" in html

    def test_output_plot_with_height(self) -> None:
        """Test output_plot with height parameter."""
        result = output_plot("plot", height="300px")
        html = str(result)
        assert "plot" in html


class TestOutputImage:
    """Tests for output_image function."""

    def test_output_image_basic(self) -> None:
        """Test basic output_image creation."""
        result = output_image("my_image")
        assert isinstance(result, Tag)

    def test_output_image_has_id(self) -> None:
        """Test output_image has correct id."""
        result = output_image("image_output")
        html = str(result)
        assert "image_output" in html

    def test_output_image_with_width(self) -> None:
        """Test output_image with width parameter."""
        result = output_image("image", width="200px")
        html = str(result)
        assert "image" in html

    def test_output_image_with_height(self) -> None:
        """Test output_image with height parameter."""
        result = output_image("image", height="150px")
        html = str(result)
        assert "image" in html


class TestOutputTable:
    """Tests for output_table function."""

    def test_output_table_basic(self) -> None:
        """Test basic output_table creation."""
        result = output_table("my_table")
        assert isinstance(result, Tag)

    def test_output_table_has_id(self) -> None:
        """Test output_table has correct id."""
        result = output_table("table_output")
        html = str(result)
        assert "table_output" in html
