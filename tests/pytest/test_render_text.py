"""Tests for shiny.render module - text, code, and plot renderers."""

from shiny.render import code, text


class TestTextRenderer:
    """Tests for the text renderer."""

    def test_text_renderer_class_exists(self):
        """Test that text renderer class exists."""
        assert text is not None

    def test_text_renderer_is_class(self):
        """Test that text is a class."""
        assert isinstance(text, type)

    def test_text_renderer_has_docstring(self):
        """Test that text renderer has documentation."""
        assert text.__doc__ is not None


class TestCodeRenderer:
    """Tests for the code renderer."""

    def test_code_renderer_class_exists(self):
        """Test that code renderer class exists."""
        assert code is not None

    def test_code_renderer_is_class(self):
        """Test that code is a class."""
        assert isinstance(code, type)

    def test_code_renderer_has_docstring(self):
        """Test that code renderer has documentation."""
        assert code.__doc__ is not None
