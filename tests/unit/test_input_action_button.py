"""Unit tests for shiny.ui._input_action_button module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import input_action_button, input_action_link


class TestInputActionButton:
    """Tests for input_action_button function."""

    def test_basic_action_button(self) -> None:
        """Test basic action button creation."""
        result = input_action_button("btn", "Click me")
        assert isinstance(result, Tag)
        html = str(result)
        assert "btn" in html
        assert "Click me" in html

    def test_action_button_returns_tag(self) -> None:
        """Test that action button returns a Tag."""
        result = input_action_button("btn", "Label")
        assert isinstance(result, Tag)

    def test_action_button_with_icon(self) -> None:
        """Test action button with icon."""
        icon = tags.i(class_="fa fa-play")
        result = input_action_button("btn", "Play", icon=icon)
        html = str(result)
        assert "fa-play" in html

    def test_action_button_with_width(self) -> None:
        """Test action button with width."""
        result = input_action_button("btn", "Button", width="200px")
        html = str(result)
        assert "200px" in html

    def test_action_button_disabled(self) -> None:
        """Test action button with disabled state."""
        result = input_action_button("btn", "Disabled", disabled=True)
        html = str(result)
        assert "disabled" in html.lower()

    def test_action_button_not_disabled(self) -> None:
        """Test action button without disabled state."""
        result = input_action_button("btn", "Enabled", disabled=False)
        html = str(result)
        assert "btn" in html

    def test_action_button_has_type(self) -> None:
        """Test action button has type=button."""
        result = input_action_button("btn", "Button")
        html = str(result)
        assert 'type="button"' in html

    def test_action_button_has_action_button_class(self) -> None:
        """Test action button has action-button class."""
        result = input_action_button("btn", "Button")
        html = str(result)
        assert "action-button" in html

    def test_action_button_has_btn_class(self) -> None:
        """Test action button has btn class."""
        result = input_action_button("btn", "Button")
        html = str(result)
        assert "btn" in html

    def test_action_button_with_kwargs(self) -> None:
        """Test action button with custom kwargs."""
        result = input_action_button("btn", "Button", class_="extra-class")
        html = str(result)
        assert "extra-class" in html

    def test_action_button_no_label(self) -> None:
        """Test action button with None label."""
        result = input_action_button("btn", None)
        html = str(result)
        assert "btn" in html


class TestInputActionLink:
    """Tests for input_action_link function."""

    def test_basic_action_link(self) -> None:
        """Test basic action link creation."""
        result = input_action_link("link", "Click me")
        assert isinstance(result, Tag)
        html = str(result)
        assert "link" in html
        assert "Click me" in html

    def test_action_link_returns_tag(self) -> None:
        """Test that action link returns a Tag."""
        result = input_action_link("link", "Label")
        assert isinstance(result, Tag)

    def test_action_link_with_icon(self) -> None:
        """Test action link with icon."""
        icon = tags.i(class_="fa fa-arrow-right")
        result = input_action_link("link", "Next", icon=icon)
        html = str(result)
        assert "fa-arrow-right" in html

    def test_action_link_has_action_link_class(self) -> None:
        """Test action link has action-link class."""
        result = input_action_link("link", "Link")
        html = str(result)
        assert "action-link" in html

    def test_action_link_has_action_button_class(self) -> None:
        """Test action link has action-button class."""
        result = input_action_link("link", "Link")
        html = str(result)
        assert "action-button" in html

    def test_action_link_is_anchor(self) -> None:
        """Test action link is an anchor tag."""
        result = input_action_link("link", "Link")
        assert result.name == "a"

    def test_action_link_with_kwargs(self) -> None:
        """Test action link with custom kwargs."""
        result = input_action_link("link", "Link", class_="custom-link")
        html = str(result)
        assert "custom-link" in html

    def test_action_link_no_label(self) -> None:
        """Test action link with None label."""
        result = input_action_link("link", None)
        html = str(result)
        assert "link" in html
