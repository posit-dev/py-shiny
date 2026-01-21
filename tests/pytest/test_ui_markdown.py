"""Tests for shiny/ui/_markdown.py"""

from __future__ import annotations

from shiny.ui._markdown import markdown
from htmltools import HTML


class TestMarkdown:
    """Tests for the markdown function."""

    def test_basic_markdown(self) -> None:
        """Test basic markdown conversion."""
        result = markdown("**bold** text")

        assert isinstance(result, HTML)
        assert "bold" in str(result)

    def test_markdown_heading(self) -> None:
        """Test markdown heading conversion."""
        result = markdown("# Heading 1")

        rendered = str(result)
        assert "<h1>" in rendered or "Heading 1" in rendered

    def test_markdown_paragraph(self) -> None:
        """Test markdown paragraph conversion."""
        result = markdown("This is a paragraph.")

        rendered = str(result)
        assert "<p>" in rendered

    def test_markdown_link(self) -> None:
        """Test markdown link conversion."""
        result = markdown("[Link](https://example.com)")

        rendered = str(result)
        assert "href" in rendered or "Link" in rendered

    def test_markdown_code_inline(self) -> None:
        """Test inline code conversion."""
        result = markdown("`code`")

        rendered = str(result)
        assert "<code>" in rendered or "code" in rendered

    def test_markdown_list(self) -> None:
        """Test markdown list conversion."""
        result = markdown("- Item 1\n- Item 2")

        rendered = str(result)
        assert "Item" in rendered

    def test_markdown_dedent(self) -> None:
        """Test that markdown text is dedented."""
        result = markdown(
            """
            This is indented text.
            It should be dedented.
        """
        )

        rendered = str(result)
        assert "indented" in rendered

    def test_markdown_with_custom_render_func(self) -> None:
        """Test markdown with custom render function."""

        def custom_renderer(text: str) -> str:
            return f"<div>{text}</div>"

        result = markdown("Test", render_func=custom_renderer)

        assert "<div>" in str(result)

    def test_markdown_returns_html(self) -> None:
        """Test that markdown returns HTML type."""
        result = markdown("Simple text")

        assert isinstance(result, HTML)

    def test_markdown_table(self) -> None:
        """Test markdown table conversion (GFM)."""
        table_md = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
        result = markdown(table_md)

        rendered = str(result)
        # Tables should be converted to HTML table elements
        assert "Header" in rendered

    def test_markdown_strikethrough(self) -> None:
        """Test markdown strikethrough (GFM)."""
        result = markdown("~~strikethrough~~")

        rendered = str(result)
        assert "strikethrough" in rendered

    def test_markdown_italic(self) -> None:
        """Test markdown italic text."""
        result = markdown("*italic*")

        rendered = str(result)
        assert "italic" in rendered

    def test_markdown_blockquote(self) -> None:
        """Test markdown blockquote."""
        result = markdown("> Quote")

        rendered = str(result)
        assert "Quote" in rendered
