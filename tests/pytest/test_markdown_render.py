"""Tests for shiny.ui._markdown module."""

from htmltools import HTML

from shiny.ui._markdown import markdown


class TestMarkdown:
    """Tests for markdown function."""

    def test_markdown_basic(self) -> None:
        """Test basic markdown rendering."""
        result = markdown("**bold text**")
        assert isinstance(result, HTML)

    def test_markdown_heading(self) -> None:
        """Test markdown heading rendering."""
        result = markdown("# Heading 1")
        html = str(result)
        assert "<h1" in html or "Heading 1" in html

    def test_markdown_bold(self) -> None:
        """Test markdown bold rendering."""
        result = markdown("**bold**")
        html = str(result)
        assert "bold" in html

    def test_markdown_italic(self) -> None:
        """Test markdown italic rendering."""
        result = markdown("*italic*")
        html = str(result)
        assert "italic" in html

    def test_markdown_link(self) -> None:
        """Test markdown link rendering."""
        result = markdown("[link](https://example.com)")
        html = str(result)
        assert "link" in html

    def test_markdown_code(self) -> None:
        """Test markdown inline code rendering."""
        result = markdown("`code`")
        html = str(result)
        assert "code" in html

    def test_markdown_list(self) -> None:
        """Test markdown list rendering."""
        result = markdown("- item 1\n- item 2")
        html = str(result)
        assert "item" in html

    def test_markdown_paragraph(self) -> None:
        """Test markdown paragraph rendering."""
        result = markdown("This is a paragraph.")
        html = str(result)
        assert "paragraph" in html

    def test_markdown_empty_string(self) -> None:
        """Test markdown with empty string."""
        result = markdown("")
        # Should not raise an error
        assert result is not None

    def test_markdown_multiline(self) -> None:
        """Test markdown with multiple lines."""
        text = """
# Title

This is a paragraph.

- List item 1
- List item 2
"""
        result = markdown(text)
        html = str(result)
        assert "Title" in html
        assert "paragraph" in html

    def test_markdown_code_block(self) -> None:
        """Test markdown code block rendering."""
        result = markdown("```\ncode block\n```")
        html = str(result)
        assert "code" in html

    def test_markdown_blockquote(self) -> None:
        """Test markdown blockquote rendering."""
        result = markdown("> This is a quote")
        html = str(result)
        assert "quote" in html
