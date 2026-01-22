"""Tests for shiny/ui/_markdown_stream.py - Markdown stream exports."""

from shiny.ui._markdown_stream import (
    MarkdownStream,
    output_markdown_stream,
    __all__,
)


class TestMarkdownStreamExports:
    """Tests for markdown stream exports."""

    def test_output_markdown_stream_exported(self):
        """Test output_markdown_stream is exported."""
        assert output_markdown_stream is not None
        assert callable(output_markdown_stream)

    def test_markdownstream_exported(self):
        """Test MarkdownStream is exported."""
        assert MarkdownStream is not None


class TestMarkdownStreamAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(__all__, tuple)

    def test_all_contains_output_markdown_stream(self):
        """Test __all__ contains output_markdown_stream."""
        assert "output_markdown_stream" in __all__

    def test_all_contains_markdownstream(self):
        """Test __all__ contains MarkdownStream."""
        assert "MarkdownStream" in __all__
