"""Tests for shiny/ui/_output.py - Output containers."""

from shiny.ui._output import (
    output_code,
    output_image,
    output_plot,
    output_table,
    output_text,
    output_text_verbatim,
    output_ui,
)


class TestOutputPlot:
    """Tests for output_plot function."""

    def test_output_plot_basic(self):
        """Test basic output_plot."""
        result = output_plot("my_plot")
        html = str(result)
        assert "shiny-plot-output" in html
        assert 'id="my_plot"' in html

    def test_output_plot_with_size(self):
        """Test output_plot with custom size."""
        result = output_plot("my_plot", width="50%", height="300px")
        html = str(result)
        assert "width:50%" in html
        assert "height:300px" in html

    def test_output_plot_numeric_size(self):
        """Test output_plot with numeric size."""
        result = output_plot("my_plot", width=400, height=300)
        html = str(result)
        assert "width:400px" in html
        assert "height:300px" in html

    def test_output_plot_inline(self):
        """Test output_plot with inline=True."""
        result = output_plot("my_plot", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_plot_with_click(self):
        """Test output_plot with click enabled."""
        result = output_plot("my_plot", click=True)
        html = str(result)
        assert "data-click-id" in html

    def test_output_plot_with_dblclick(self):
        """Test output_plot with dblclick enabled."""
        result = output_plot("my_plot", dblclick=True)
        html = str(result)
        assert "data-dblclick-id" in html

    def test_output_plot_with_hover(self):
        """Test output_plot with hover enabled."""
        result = output_plot("my_plot", hover=True)
        html = str(result)
        assert "data-hover-id" in html

    def test_output_plot_with_brush(self):
        """Test output_plot with brush enabled."""
        result = output_plot("my_plot", brush=True)
        html = str(result)
        assert "data-brush-id" in html

    def test_output_plot_fill_default_true_when_not_inline(self):
        """Test fill defaults to True when not inline."""
        result = output_plot("my_plot", inline=False)
        html = str(result)
        # Should be fillable when not inline (default behavior)
        assert "html-fill-item" in html

    def test_output_plot_fill_default_false_when_inline(self):
        """Test fill defaults to False when inline."""
        result = output_plot("my_plot", inline=True)
        html = str(result)
        # Should not be fillable when inline
        assert "html-fill-item" not in html


class TestOutputImage:
    """Tests for output_image function."""

    def test_output_image_basic(self):
        """Test basic output_image."""
        result = output_image("my_image")
        html = str(result)
        assert "shiny-image-output" in html
        assert 'id="my_image"' in html

    def test_output_image_default_size(self):
        """Test output_image default size."""
        result = output_image("my_image")
        html = str(result)
        assert "width:100%" in html
        assert "height:400px" in html

    def test_output_image_inline(self):
        """Test output_image inline."""
        result = output_image("my_image", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_image_fill(self):
        """Test output_image fill."""
        result = output_image("my_image", fill=True)
        html = str(result)
        assert "html-fill-item" in html


class TestOutputText:
    """Tests for output_text function."""

    def test_output_text_basic(self):
        """Test basic output_text."""
        result = output_text("my_text")
        html = str(result)
        assert "shiny-text-output" in html
        assert 'id="my_text"' in html
        assert "<div" in html

    def test_output_text_inline(self):
        """Test output_text inline."""
        result = output_text("my_text", inline=True)
        html = str(result)
        assert "<span" in html


class TestOutputCode:
    """Tests for output_code function."""

    def test_output_code_basic(self):
        """Test basic output_code."""
        result = output_code("my_code")
        html = str(result)
        assert "shiny-text-output" in html
        assert 'id="my_code"' in html
        assert "<pre" in html

    def test_output_code_with_placeholder(self):
        """Test output_code with placeholder."""
        result = output_code("my_code", placeholder=True)
        html = str(result)
        assert "noplaceholder" not in html

    def test_output_code_without_placeholder(self):
        """Test output_code without placeholder."""
        result = output_code("my_code", placeholder=False)
        html = str(result)
        assert "noplaceholder" in html


class TestOutputTextVerbatim:
    """Tests for output_text_verbatim function."""

    def test_output_text_verbatim_basic(self):
        """Test basic output_text_verbatim."""
        result = output_text_verbatim("my_text")
        html = str(result)
        assert "shiny-text-output" in html
        assert 'id="my_text"' in html
        assert "<pre" in html

    def test_output_text_verbatim_default_no_placeholder(self):
        """Test output_text_verbatim default has no placeholder."""
        result = output_text_verbatim("my_text")
        html = str(result)
        assert "noplaceholder" in html

    def test_output_text_verbatim_with_placeholder(self):
        """Test output_text_verbatim with placeholder."""
        result = output_text_verbatim("my_text", placeholder=True)
        html = str(result)
        assert "noplaceholder" not in html


class TestOutputTable:
    """Tests for output_table function."""

    def test_output_table_basic(self):
        """Test basic output_table."""
        result = output_table("my_table")
        html = str(result)
        assert "shiny-html-output" in html
        assert 'id="my_table"' in html

    def test_output_table_with_kwargs(self):
        """Test output_table with additional attributes."""
        result = output_table("my_table", style="margin: 10px;")
        html = str(result)
        assert "margin: 10px" in html


class TestOutputUi:
    """Tests for output_ui function."""

    def test_output_ui_basic(self):
        """Test basic output_ui."""
        result = output_ui("my_ui")
        html = str(result)
        assert "shiny-html-output" in html
        assert 'id="my_ui"' in html

    def test_output_ui_inline(self):
        """Test output_ui inline."""
        result = output_ui("my_ui", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_ui_fill(self):
        """Test output_ui fill."""
        result = output_ui("my_ui", fill=True)
        html = str(result)
        assert "html-fill-item" in html

    def test_output_ui_fillable(self):
        """Test output_ui fillable."""
        result = output_ui("my_ui", fillable=True)
        html = str(result)
        assert "html-fill-container" in html

    def test_output_ui_with_kwargs(self):
        """Test output_ui with additional attributes."""
        result = output_ui("my_ui", class_="custom-class")
        html = str(result)
        assert "custom-class" in html
