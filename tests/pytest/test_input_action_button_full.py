"""Tests for shiny/ui/_input_action_button.py module."""

from shiny.ui._input_action_button import input_action_button, input_action_link


class TestInputActionButton:
    """Tests for input_action_button function."""

    def test_input_action_button_is_callable(self):
        """Test input_action_button is callable."""
        assert callable(input_action_button)

    def test_input_action_button_returns_tag(self):
        """Test input_action_button returns a Tag."""
        from htmltools import Tag

        result = input_action_button("my_btn", "Click me")
        assert isinstance(result, Tag)

    def test_input_action_button_with_class(self):
        """Test input_action_button with class_ parameter."""
        from htmltools import Tag

        result = input_action_button("my_btn", "Click me", class_="btn-primary")
        assert isinstance(result, Tag)

    def test_input_action_button_with_icon(self):
        """Test input_action_button with icon parameter."""
        from htmltools import Tag

        icon = Tag("i", class_="fa fa-play")
        result = input_action_button("my_btn", "Click me", icon=icon)
        assert isinstance(result, Tag)


class TestInputActionLink:
    """Tests for input_action_link function."""

    def test_input_action_link_is_callable(self):
        """Test input_action_link is callable."""
        assert callable(input_action_link)

    def test_input_action_link_returns_tag(self):
        """Test input_action_link returns a Tag."""
        from htmltools import Tag

        result = input_action_link("my_link", "Click me")
        assert isinstance(result, Tag)


class TestActionButtonExported:
    """Tests for action button functions export."""

    def test_input_action_button_in_ui(self):
        """Test input_action_button is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_action_button")

    def test_input_action_link_in_ui(self):
        """Test input_action_link is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_action_link")
