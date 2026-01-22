"""Tests for shiny/render/_render.py module."""

from shiny.render._render import code, text, ui


class TestRenderText:
    """Tests for render.text decorator."""

    def test_text_is_callable(self):
        """Test text is callable."""
        assert callable(text)


class TestRenderUi:
    """Tests for render.ui decorator."""

    def test_ui_is_callable(self):
        """Test ui is callable."""
        assert callable(ui)


class TestRenderCode:
    """Tests for render.code decorator."""

    def test_code_is_callable(self):
        """Test code is callable."""
        assert callable(code)


class TestRenderExported:
    """Tests for render functions export."""

    def test_text_in_render(self):
        """Test text is in render module."""
        from shiny import render

        assert hasattr(render, "text")

    def test_ui_in_render(self):
        """Test ui is in render module."""
        from shiny import render

        assert hasattr(render, "ui")

    def test_code_in_render(self):
        """Test code is in render module."""
        from shiny import render

        assert hasattr(render, "code")
