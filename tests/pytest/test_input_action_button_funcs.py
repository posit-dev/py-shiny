"""Tests for shiny.ui._input_action_button module."""

from htmltools import Tag

from shiny.ui._input_action_button import input_action_button, input_action_link


class TestInputActionButton:
    """Tests for input_action_button function."""

    def test_input_action_button_basic(self) -> None:
        """Test basic input_action_button creation."""
        result = input_action_button("my_button", "Click me")
        assert isinstance(result, Tag)

    def test_input_action_button_has_id(self) -> None:
        """Test input_action_button has correct id."""
        result = input_action_button("button_id", "Button")
        html = str(result)
        assert "button_id" in html

    def test_input_action_button_with_label(self) -> None:
        """Test input_action_button with label."""
        result = input_action_button("button", "Submit Form")
        html = str(result)
        assert "Submit Form" in html

    def test_input_action_button_button_tag(self) -> None:
        """Test input_action_button returns button tag."""
        result = input_action_button("button", "Label")
        assert result.name == "button"

    def test_input_action_button_with_width(self) -> None:
        """Test input_action_button with width parameter."""
        result = input_action_button("button", "Label", width="200px")
        html = str(result)
        assert "button" in html

    def test_input_action_button_with_class(self) -> None:
        """Test input_action_button with class_ parameter."""
        result = input_action_button("button", "Label", class_="btn-primary")
        html = str(result)
        assert "btn-primary" in html

    def test_input_action_button_btn_class(self) -> None:
        """Test input_action_button has btn class."""
        result = input_action_button("button", "Label")
        html = str(result)
        assert "btn" in html


class TestInputActionLink:
    """Tests for input_action_link function."""

    def test_input_action_link_basic(self) -> None:
        """Test basic input_action_link creation."""
        result = input_action_link("my_link", "Click here")
        assert isinstance(result, Tag)

    def test_input_action_link_has_id(self) -> None:
        """Test input_action_link has correct id."""
        result = input_action_link("link_id", "Link")
        html = str(result)
        assert "link_id" in html

    def test_input_action_link_with_label(self) -> None:
        """Test input_action_link with label."""
        result = input_action_link("link", "Learn more")
        html = str(result)
        assert "Learn more" in html

    def test_input_action_link_anchor_tag(self) -> None:
        """Test input_action_link returns anchor tag."""
        result = input_action_link("link", "Label")
        assert result.name == "a"

    def test_input_action_link_href_attribute(self) -> None:
        """Test input_action_link has href attribute."""
        result = input_action_link("link", "Label")
        html = str(result)
        assert "href" in html
