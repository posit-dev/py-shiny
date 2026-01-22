"""Tests for shiny/ui/_input_text.py module."""

from shiny.ui._input_password import (
    input_password,
)
from shiny.ui._input_text import (
    input_text,
    input_text_area,
)


class TestInputText:
    """Tests for input_text function."""

    def test_input_text_is_callable(self):
        """Test input_text is callable."""
        assert callable(input_text)

    def test_input_text_returns_tag(self):
        """Test input_text returns a Tag."""
        from htmltools import Tag

        result = input_text("my_text", "Enter text")
        assert isinstance(result, Tag)

    def test_input_text_with_value(self):
        """Test input_text with value parameter."""
        from htmltools import Tag

        result = input_text("my_text", "Enter text", value="Hello")
        assert isinstance(result, Tag)

    def test_input_text_with_placeholder(self):
        """Test input_text with placeholder parameter."""
        from htmltools import Tag

        result = input_text("my_text", "Enter text", placeholder="Type here...")
        assert isinstance(result, Tag)


class TestInputTextArea:
    """Tests for input_text_area function."""

    def test_input_text_area_is_callable(self):
        """Test input_text_area is callable."""
        assert callable(input_text_area)

    def test_input_text_area_returns_tag(self):
        """Test input_text_area returns a Tag."""
        from htmltools import Tag

        result = input_text_area("my_textarea", "Enter text")
        assert isinstance(result, Tag)

    def test_input_text_area_with_rows(self):
        """Test input_text_area with rows parameter."""
        from htmltools import Tag

        result = input_text_area("my_textarea", "Enter text", rows=10)
        assert isinstance(result, Tag)


class TestInputPassword:
    """Tests for input_password function."""

    def test_input_password_is_callable(self):
        """Test input_password is callable."""
        assert callable(input_password)

    def test_input_password_returns_tag(self):
        """Test input_password returns a Tag."""
        from htmltools import Tag

        result = input_password("my_password", "Enter password")
        assert isinstance(result, Tag)


class TestInputTextExported:
    """Tests for text input functions export."""

    def test_input_text_in_ui(self):
        """Test input_text is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_text")

    def test_input_text_area_in_ui(self):
        """Test input_text_area is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_text_area")

    def test_input_password_in_ui(self):
        """Test input_password is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_password")
