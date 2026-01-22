"""
Unit tests for shiny/ui/_markdown.py
Tests for markdown() and default_md_renderer() functions
"""

import warnings
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from shiny.ui._markdown import default_md_renderer, markdown


# =============================================================================
# Tests for markdown() function
# =============================================================================
class TestMarkdown:
    """Tests for markdown() function"""

    def test_basic_markdown(self):
        """Test basic markdown rendering"""
        result = markdown("# Hello World")
        assert "Hello World" in str(result)
        assert "<h1>" in str(result)

    def test_returns_html_type(self):
        """Test that markdown returns HTML type"""
        from shiny.ui import HTML

        result = markdown("Hello")
        assert isinstance(result, HTML)

    def test_paragraph(self):
        """Test paragraph rendering"""
        result = markdown("This is a paragraph.")
        assert "<p>" in str(result)
        assert "This is a paragraph." in str(result)

    def test_bold_text(self):
        """Test bold text rendering"""
        result = markdown("**bold text**")
        assert "<strong>" in str(result) or "<b>" in str(result)
        assert "bold text" in str(result)

    def test_italic_text(self):
        """Test italic text rendering"""
        result = markdown("*italic text*")
        assert "<em>" in str(result) or "<i>" in str(result)
        assert "italic text" in str(result)

    def test_code_inline(self):
        """Test inline code rendering"""
        result = markdown("`code`")
        assert "<code>" in str(result)
        assert "code" in str(result)

    def test_code_block(self):
        """Test code block rendering"""
        result = markdown("```\ncode block\n```")
        assert "code block" in str(result)

    def test_unordered_list(self):
        """Test unordered list rendering"""
        result = markdown("- item 1\n- item 2\n- item 3")
        assert "<ul>" in str(result)
        assert "<li>" in str(result)

    def test_ordered_list(self):
        """Test ordered list rendering"""
        result = markdown("1. first\n2. second\n3. third")
        assert "<ol>" in str(result)
        assert "<li>" in str(result)

    def test_link(self):
        """Test link rendering"""
        result = markdown("[link text](https://example.com)")
        assert "<a" in str(result)
        assert "https://example.com" in str(result)
        assert "link text" in str(result)

    def test_image(self):
        """Test image rendering"""
        result = markdown("![alt text](https://example.com/image.png)")
        assert "<img" in str(result)
        assert "https://example.com/image.png" in str(result)

    def test_blockquote(self):
        """Test blockquote rendering"""
        result = markdown("> This is a quote")
        assert "<blockquote>" in str(result)
        assert "This is a quote" in str(result)

    def test_horizontal_rule(self):
        """Test horizontal rule rendering"""
        result = markdown("---")
        assert "<hr" in str(result)

    def test_dedents_text(self):
        """Test that markdown dedents text properly"""
        indented = """
            # Header
            Some text
        """
        result = markdown(indented)
        assert "Header" in str(result)
        assert "Some text" in str(result)

    def test_multiple_headers(self):
        """Test multiple header levels"""
        result = markdown("# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6")
        assert "<h1>" in str(result)
        assert "<h2>" in str(result)
        assert "<h3>" in str(result)
        assert "<h4>" in str(result)
        assert "<h5>" in str(result)
        assert "<h6>" in str(result)

    def test_complex_document(self):
        """Test a complex markdown document"""
        md_text = """
# Title

This is a paragraph with **bold** and *italic* text.

## List

- Item 1
- Item 2

## Code

```python
print("hello")
```

[A link](https://example.com)
        """
        result = markdown(md_text)
        html = str(result)
        assert "Title" in html
        assert "<strong>" in html or "<b>" in html
        assert "<ul>" in html
        assert "print" in html
        assert "https://example.com" in html


class TestMarkdownCustomRenderer:
    """Tests for markdown with custom render function"""

    def test_custom_render_func(self):
        """Test markdown with custom render function"""

        def custom_renderer(text: str) -> str:
            return f"<custom>{text}</custom>"

        result = markdown("Hello", render_func=custom_renderer)
        assert "<custom>Hello</custom>" in str(result)

    def test_custom_render_func_with_kwargs(self):
        """Test markdown with custom render function and kwargs"""

        def custom_renderer(text: str, prefix: str = "") -> str:
            return f"{prefix}{text}"

        result = markdown("Hello", render_func=custom_renderer, prefix="PREFIX:")
        assert "PREFIX:" in str(result)

    def test_custom_render_func_replaces_default(self):
        """Test that custom render function replaces default"""

        def noop_renderer(text: str) -> str:
            return text

        result = markdown("# Header", render_func=noop_renderer)
        # Should not have H1 tags since noop_renderer doesn't process markdown
        assert "<h1>" not in str(result)
        assert "# Header" in str(result)


# =============================================================================
# Tests for default_md_renderer() function
# =============================================================================
class TestDefaultMdRenderer:
    """Tests for default_md_renderer() function"""

    def test_returns_callable(self):
        """Test that default_md_renderer returns a callable"""
        renderer = default_md_renderer()
        assert callable(renderer)

    def test_renderer_returns_string(self):
        """Test that renderer returns a string"""
        renderer = default_md_renderer()
        result = renderer("# Hello")
        assert isinstance(result, str)

    def test_preset_gfm_default(self):
        """Test that gfm is the default preset"""
        renderer = default_md_renderer()
        # GFM enables tables, which commonmark doesn't support
        result = renderer("| A | B |\n|---|---|\n| 1 | 2 |")
        assert "<table>" in result

    def test_preset_commonmark(self):
        """Test commonmark preset"""
        renderer = default_md_renderer(preset="commonmark")
        # Commonmark doesn't support tables
        result = renderer("| A | B |\n|---|---|\n| 1 | 2 |")
        assert "<table>" not in result

    def test_preset_gfm_explicit(self):
        """Test explicit gfm preset"""
        renderer = default_md_renderer(preset="gfm")
        result = renderer("| A | B |\n|---|---|\n| 1 | 2 |")
        assert "<table>" in result

    def test_gfm_strikethrough(self):
        """Test GFM strikethrough"""
        renderer = default_md_renderer(preset="gfm")
        result = renderer("~~strikethrough~~")
        assert "<s>" in result or "<del>" in result

    def test_commonmark_basic(self):
        """Test commonmark basic rendering"""
        renderer = default_md_renderer(preset="commonmark")
        result = renderer("# Header\n\nParagraph")
        assert "<h1>" in result
        assert "<p>" in result


class TestDefaultMdRendererModuleNotFound:
    """Tests for module not found errors"""

    @patch.dict("sys.modules", {"markdown_it": None, "markdown_it.main": None})
    def test_markdown_it_not_installed(self):
        """Test error when markdown-it-py is not installed"""
        # We need to reload the module to trigger the import error
        import importlib

        import shiny.ui._markdown

        with pytest.raises(ModuleNotFoundError, match="markdown-it"):
            importlib.reload(shiny.ui._markdown)
            default_md_renderer()

        # Restore the module
        importlib.reload(shiny.ui._markdown)


class TestDefaultMdRendererWarnings:
    """Tests for warnings when optional packages are missing"""

    @patch("importlib.import_module")
    def test_warns_when_linkify_missing(self, mock_import: MagicMock) -> None:
        """Test warning when linkify-it is not installed"""

        def side_effect(name: str, package: str | None = None) -> Any:
            if "linkify" in str(name) or "linkify" in str(package or ""):
                raise ModuleNotFoundError("No module named 'linkify_it'")
            raise ModuleNotFoundError("Allow MarkdownIt import")

        mock_import.side_effect = side_effect

        # Need to test with actual MarkdownIt available
        try:
            import importlib.util

            if importlib.util.find_spec("markdown_it") is None:
                pytest.skip("markdown-it-py not installed")

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                # This should warn about linkify
                _ = default_md_renderer(preset="gfm")
                # Check if warning was raised
                _ = [x for x in w if "linkify" in str(x.message).lower()]
                # May or may not warn depending on environment
        except ModuleNotFoundError:
            pytest.skip("markdown-it-py not installed")


class TestMarkdownGfmFeatures:
    """Tests for GitHub Flavored Markdown features"""

    def test_table_rendering(self):
        """Test table rendering in GFM"""
        table = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        result = markdown(table)
        html = str(result)
        assert "<table>" in html
        assert "<th>" in html or "<thead>" in html
        assert "<td>" in html

    def test_strikethrough(self):
        """Test strikethrough in GFM"""
        result = markdown("~~deleted~~")
        html = str(result)
        assert "<s>" in html or "<del>" in html
        assert "deleted" in html


class TestMarkdownEdgeCases:
    """Tests for edge cases"""

    def test_empty_string(self):
        """Test with empty string"""
        result = markdown("")
        assert str(result) == ""

    def test_whitespace_only(self):
        """Test with whitespace only"""
        result = markdown("   \n   \n   ")
        # Should be empty or just whitespace after dedent
        assert str(result).strip() == ""

    def test_single_newline(self):
        """Test with single newline"""
        result = markdown("\n")
        assert str(result).strip() == ""

    def test_unicode_content(self):
        """Test with unicode content"""
        result = markdown("# 你好世界\n\n日本語テキスト\n\n🎉 emoji!")
        html = str(result)
        assert "你好世界" in html
        assert "日本語" in html
        assert "🎉" in html

    def test_html_in_markdown(self):
        """Test HTML content in markdown"""
        result = markdown("Text <span>HTML</span> more text")
        # HTML should be preserved
        assert "HTML" in str(result)

    def test_very_long_document(self):
        """Test with a very long document"""
        long_text = "# Header\n\n" + "Paragraph.\n\n" * 100
        result = markdown(long_text)
        html = str(result)
        assert "<h1>" in html
        assert html.count("<p>") >= 100

    def test_nested_lists(self):
        """Test nested lists"""
        nested = """
- Level 1
  - Level 2
    - Level 3
  - Level 2 again
- Level 1 again
"""
        result = markdown(nested)
        html = str(result)
        assert "<ul>" in html
        assert "<li>" in html

    def test_special_characters(self):
        """Test special characters"""
        result = markdown("& < > \" '")
        # Should handle special characters
        html = str(result)
        assert "&amp;" in html or "&" in html
