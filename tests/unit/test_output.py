"""Tests for shiny/ui/_output.py"""

from htmltools import Tag

from shiny.ui import (
    output_code,
    output_image,
    output_plot,
    output_table,
    output_text,
    output_text_verbatim,
    output_ui,
)


class TestOutputPlot:
    """Tests for the output_plot function."""

    def test_basic_output_plot(self):
        """Test basic plot output creation."""
        result = output_plot("my_plot")
        html = str(result)
        assert 'id="my_plot"' in html
        assert "shiny-plot-output" in html
        assert "shiny-image-output" in html

    def test_output_plot_returns_tag(self):
        """Test output_plot returns a Tag."""
        result = output_plot("plot")
        assert isinstance(result, Tag)

    def test_output_plot_default_dimensions(self):
        """Test plot output with default dimensions."""
        result = output_plot("plot")
        html = str(result)
        assert "width:100%" in html
        assert "height:400px" in html

    def test_output_plot_custom_width(self):
        """Test plot output with custom width."""
        result = output_plot("plot", width="500px")
        html = str(result)
        assert "width:500px" in html

    def test_output_plot_custom_height(self):
        """Test plot output with custom height."""
        result = output_plot("plot", height="600px")
        html = str(result)
        assert "height:600px" in html

    def test_output_plot_numeric_dimensions(self):
        """Test plot output with numeric dimensions."""
        result = output_plot("plot", width=400, height=300)
        html = str(result)
        assert "width:400px" in html
        assert "height:300px" in html

    def test_output_plot_inline_false(self):
        """Test plot output not inline (default)."""
        result = output_plot("plot")
        html = str(result)
        assert "<div" in html

    def test_output_plot_inline_true(self):
        """Test plot output inline."""
        result = output_plot("plot", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_plot_click_true(self):
        """Test plot output with click enabled."""
        result = output_plot("plot", click=True)
        html = str(result)
        assert "data-click-id" in html or "plot_click" in html

    def test_output_plot_hover_true(self):
        """Test plot output with hover enabled."""
        result = output_plot("plot", hover=True)
        html = str(result)
        assert "data-hover-id" in html or "plot_hover" in html

    def test_output_plot_dblclick_true(self):
        """Test plot output with double click enabled."""
        result = output_plot("plot", dblclick=True)
        html = str(result)
        assert "data-dblclick-id" in html or "plot_dblclick" in html

    def test_output_plot_brush_true(self):
        """Test plot output with brush enabled."""
        result = output_plot("plot", brush=True)
        html = str(result)
        assert "data-brush-id" in html or "plot_brush" in html


class TestOutputImage:
    """Tests for the output_image function."""

    def test_basic_output_image(self):
        """Test basic image output creation."""
        result = output_image("my_img")
        html = str(result)
        assert 'id="my_img"' in html
        assert "shiny-image-output" in html

    def test_output_image_returns_tag(self):
        """Test output_image returns a Tag."""
        result = output_image("img")
        assert isinstance(result, Tag)

    def test_output_image_default_dimensions(self):
        """Test image output with default dimensions."""
        result = output_image("img")
        html = str(result)
        assert "width:100%" in html
        assert "height:400px" in html

    def test_output_image_custom_dimensions(self):
        """Test image output with custom dimensions."""
        result = output_image("img", width="200px", height="150px")
        html = str(result)
        assert "width:200px" in html
        assert "height:150px" in html

    def test_output_image_inline(self):
        """Test image output inline."""
        result = output_image("img", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_image_not_inline(self):
        """Test image output not inline."""
        result = output_image("img", inline=False)
        html = str(result)
        assert "<div" in html


class TestOutputText:
    """Tests for the output_text function."""

    def test_basic_output_text(self):
        """Test basic text output creation."""
        result = output_text("my_text")
        html = str(result)
        assert 'id="my_text"' in html
        assert "shiny-text-output" in html

    def test_output_text_returns_tag(self):
        """Test output_text returns a Tag."""
        result = output_text("text")
        assert isinstance(result, Tag)

    def test_output_text_inline_false(self):
        """Test text output not inline (default)."""
        result = output_text("text")
        html = str(result)
        assert "<div" in html

    def test_output_text_inline_true(self):
        """Test text output inline."""
        result = output_text("text", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_text_custom_container(self):
        """Test text output with custom container."""
        from htmltools import tags

        result = output_text("text", container=tags.p)
        html = str(result)
        assert "<p" in html


class TestOutputCode:
    """Tests for the output_code function."""

    def test_basic_output_code(self):
        """Test basic code output creation."""
        result = output_code("my_code")
        html = str(result)
        assert 'id="my_code"' in html
        assert "shiny-text-output" in html
        assert "<pre" in html

    def test_output_code_returns_tag(self):
        """Test output_code returns a Tag."""
        result = output_code("code")
        assert isinstance(result, Tag)

    def test_output_code_placeholder_true(self):
        """Test code output with placeholder (default)."""
        result = output_code("code")
        html = str(result)
        assert "noplaceholder" not in html

    def test_output_code_placeholder_false(self):
        """Test code output without placeholder."""
        result = output_code("code", placeholder=False)
        html = str(result)
        assert "noplaceholder" in html


class TestOutputTextVerbatim:
    """Tests for the output_text_verbatim function."""

    def test_basic_output_text_verbatim(self):
        """Test basic verbatim text output creation."""
        result = output_text_verbatim("my_verbatim")
        html = str(result)
        assert 'id="my_verbatim"' in html
        assert "shiny-text-output" in html
        assert "<pre" in html

    def test_output_text_verbatim_returns_tag(self):
        """Test output_text_verbatim returns a Tag."""
        result = output_text_verbatim("verbatim")
        assert isinstance(result, Tag)

    def test_output_text_verbatim_placeholder_false(self):
        """Test verbatim text output without placeholder (default)."""
        result = output_text_verbatim("verbatim")
        html = str(result)
        assert "noplaceholder" in html

    def test_output_text_verbatim_placeholder_true(self):
        """Test verbatim text output with placeholder."""
        result = output_text_verbatim("verbatim", placeholder=True)
        html = str(result)
        assert "noplaceholder" not in html


class TestOutputTable:
    """Tests for the output_table function."""

    def test_basic_output_table(self):
        """Test basic table output creation."""
        result = output_table("my_table")
        html = str(result)
        assert 'id="my_table"' in html
        assert "shiny-html-output" in html

    def test_output_table_returns_tag(self):
        """Test output_table returns a Tag."""
        result = output_table("table")
        assert isinstance(result, Tag)

    def test_output_table_with_kwargs(self):
        """Test table output with additional attributes."""
        result = output_table("table", class_="custom-class", data_custom="value")
        html = str(result)
        assert "custom-class" in html
        assert 'data-custom="value"' in html


class TestOutputUI:
    """Tests for the output_ui function."""

    def test_basic_output_ui(self):
        """Test basic UI output creation."""
        result = output_ui("my_ui")
        html = str(result)
        assert 'id="my_ui"' in html
        assert "shiny-html-output" in html

    def test_output_ui_returns_tag(self):
        """Test output_ui returns a Tag."""
        result = output_ui("ui")
        assert isinstance(result, Tag)

    def test_output_ui_inline_false(self):
        """Test UI output not inline (default)."""
        result = output_ui("ui")
        html = str(result)
        assert "<div" in html

    def test_output_ui_inline_true(self):
        """Test UI output inline."""
        result = output_ui("ui", inline=True)
        html = str(result)
        assert "<span" in html

    def test_output_ui_custom_container(self):
        """Test UI output with custom container."""
        from htmltools import tags

        result = output_ui("ui", container=tags.section)
        html = str(result)
        assert "<section" in html

    def test_output_ui_fill(self):
        """Test UI output with fill enabled."""
        result = output_ui("ui", fill=True)
        html = str(result)
        assert "shiny-html-output" in html
        # Fill adds certain classes/styles
        assert 'id="ui"' in html

    def test_output_ui_fillable(self):
        """Test UI output with fillable enabled."""
        result = output_ui("ui", fillable=True)
        html = str(result)
        assert "shiny-html-output" in html
        assert 'id="ui"' in html

    def test_output_ui_with_kwargs(self):
        """Test UI output with additional attributes."""
        result = output_ui("ui", class_="custom-class", data_custom="value")
        html = str(result)
        assert "custom-class" in html
        assert 'data-custom="value"' in html
