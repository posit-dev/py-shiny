"""Tests for shiny.ui._markdown module."""

from shiny.ui import markdown
from shiny.ui._markdown import default_md_renderer
from htmltools import HTML


class TestMarkdown:
    """Tests for markdown function."""

    def test_markdown_basic(self):
        """Test basic markdown conversion."""
        result = markdown("**bold**")
        assert isinstance(result, HTML)
        html_str = str(result)
        assert "<strong>" in html_str or "<b>" in html_str

    def test_markdown_italic(self):
        """Test italic markdown conversion."""
        result = markdown("*italic*")
        html_str = str(result)
        assert "<em>" in html_str or "<i>" in html_str

    def test_markdown_header(self):
        """Test header markdown conversion."""
        result = markdown("# Header")
        html_str = str(result)
        assert "<h1>" in html_str

    def test_markdown_link(self):
        """Test link markdown conversion."""
        result = markdown("[link](https://example.com)")
        html_str = str(result)
        assert "<a" in html_str
        assert "https://example.com" in html_str

    def test_markdown_list(self):
        """Test list markdown conversion."""
        result = markdown("- item 1\n- item 2")
        html_str = str(result)
        assert "<ul>" in html_str or "<li>" in html_str

    def test_markdown_code_inline(self):
        """Test inline code markdown conversion."""
        result = markdown("`code`")
        html_str = str(result)
        assert "<code>" in html_str

    def test_markdown_dedent(self):
        """Test markdown dedents text."""
        result = markdown(
            """
            # Header
            Text
            """
        )
        html_str = str(result)
        assert "<h1>" in html_str

    def test_markdown_custom_renderer(self):
        """Test markdown with custom renderer."""

        def custom_render(text: str) -> str:
            return f"<custom>{text}</custom>"

        result = markdown("test", render_func=custom_render)
        html_str = str(result)
        assert "<custom>" in html_str


class TestDefaultMdRenderer:
    """Tests for default_md_renderer function."""

    def test_default_md_renderer_gfm(self):
        """Test default renderer with gfm preset."""
        renderer = default_md_renderer(preset="gfm")
        assert callable(renderer)
        result = renderer("**bold**")
        assert "<strong>" in result

    def test_default_md_renderer_commonmark(self):
        """Test default renderer with commonmark preset."""
        renderer = default_md_renderer(preset="commonmark")
        assert callable(renderer)
        result = renderer("**bold**")
        assert "<strong>" in result
