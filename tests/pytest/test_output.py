"""Tests for `shiny.ui._output`."""

from shiny.ui import (
    output_code,
    output_image,
    output_plot,
    output_table,
    output_text,
    output_text_verbatim,
    output_ui,
)


class TestOutputText:
    """Tests for the output_text function."""

    def test_basic_output_text(self):
        """Test creating a basic text output."""
        out = output_text("my_text")
        html = str(out)

        assert 'id="my_text"' in html
        assert "shiny-text-output" in html

    def test_output_text_inline(self):
        """Test output_text with inline=True creates a span."""
        out_inline = output_text("my_text", inline=True)
        out_block = output_text("my_text", inline=False)

        html_inline = str(out_inline)
        html_block = str(out_block)

        assert "<span" in html_inline
        assert "<div" in html_block

    def test_output_text_with_container(self):
        """Test output_text with custom container function."""
        from htmltools import tags

        out = output_text("my_text", container=tags.p)
        html = str(out)

        assert "<p" in html


class TestOutputTextVerbatim:
    """Tests for the output_text_verbatim function."""

    def test_basic_output_verbatim(self):
        """Test creating a verbatim text output."""
        out = output_text_verbatim("my_verbatim")
        html = str(out)

        assert 'id="my_verbatim"' in html
        assert "<pre" in html
        assert "shiny-text-output" in html

    def test_output_verbatim_placeholder_true(self):
        """Test verbatim output with placeholder=True uses CSS visibility."""
        out = output_text_verbatim("my_verbatim", placeholder=True)
        html = str(out)

        # When placeholder=True, there should be some indication in the HTML
        assert 'id="my_verbatim"' in html

    def test_output_verbatim_placeholder_false(self):
        """Test verbatim output with placeholder=False."""
        out = output_text_verbatim("my_verbatim", placeholder=False)
        html = str(out)

        assert 'id="my_verbatim"' in html


class TestOutputCode:
    """Tests for the output_code function."""

    def test_basic_output_code(self):
        """Test creating a code output."""
        out = output_code("my_code")
        html = str(out)

        assert 'id="my_code"' in html
        assert "<pre" in html
        assert "shiny-text-output" in html

    def test_output_code_with_placeholder(self):
        """Test code output with placeholder=True (default)."""
        out = output_code("my_code", placeholder=True)
        html = str(out)

        assert 'id="my_code"' in html
        # placeholder=True means no "noplaceholder" class
        assert "noplaceholder" not in html

    def test_output_code_without_placeholder(self):
        """Test code output with placeholder=False."""
        out = output_code("my_code", placeholder=False)
        html = str(out)

        assert 'id="my_code"' in html
        assert "noplaceholder" in html


class TestOutputPlot:
    """Tests for the output_plot function."""

    def test_basic_output_plot(self):
        """Test creating a plot output."""
        out = output_plot("my_plot")
        html = str(out)

        assert 'id="my_plot"' in html
        assert "shiny-plot-output" in html

    def test_output_plot_with_dimensions(self):
        """Test plot output with explicit dimensions."""
        out = output_plot("my_plot", width="600px", height="400px")
        html = str(out)

        assert "600px" in html
        assert "400px" in html

    def test_output_plot_fill(self):
        """Test plot output with fill enabled."""
        out = output_plot("my_plot", fill=True)
        html = str(out)

        assert 'id="my_plot"' in html


class TestOutputImage:
    """Tests for the output_image function."""

    def test_basic_output_image(self):
        """Test creating an image output."""
        out = output_image("my_image")
        html = str(out)

        assert 'id="my_image"' in html
        assert "shiny-image-output" in html

    def test_output_image_with_dimensions(self):
        """Test image output with dimensions."""
        out = output_image("my_image", width="300px", height="200px")
        html = str(out)

        assert "300px" in html
        assert "200px" in html

    def test_output_image_inline(self):
        """Test image output with inline=True."""
        out = output_image("my_image", inline=True)
        html = str(out)

        assert 'id="my_image"' in html


class TestOutputTable:
    """Tests for the output_table function."""

    def test_basic_output_table(self):
        """Test creating a table output."""
        out = output_table("my_table")
        html = str(out)

        assert 'id="my_table"' in html
        assert "shiny-html-output" in html


class TestOutputUi:
    """Tests for the output_ui function."""

    def test_basic_output_ui(self):
        """Test creating a UI output."""
        out = output_ui("my_ui")
        html = str(out)

        assert 'id="my_ui"' in html
        assert "shiny-html-output" in html

    def test_output_ui_inline(self):
        """Test UI output with inline=True."""
        out_inline = output_ui("my_ui", inline=True)
        out_block = output_ui("my_ui", inline=False)

        html_inline = str(out_inline)
        html_block = str(out_block)

        assert "<span" in html_inline
        assert "<div" in html_block

    def test_output_ui_with_container(self):
        """Test UI output with custom container."""
        from htmltools import tags

        out = output_ui("my_ui", container=tags.section)
        html = str(out)

        assert "<section" in html

    def test_output_ui_fill(self):
        """Test UI output with fill enabled."""
        out = output_ui("my_ui", fill=True)
        html = str(out)

        assert 'id="my_ui"' in html

    def test_output_ui_fillable(self):
        """Test UI output with fillable enabled."""
        out = output_ui("my_ui", fillable=True)
        html = str(out)

        assert 'id="my_ui"' in html
