"""Tests for input_action_button and input_action_link functions."""

from htmltools import Tag, tags

from shiny.ui._input_action_button import input_action_button, input_action_link


class TestInputActionButton:
    """Tests for the input_action_button function."""

    def test_action_button_basic(self):
        """Test basic action button creation."""
        result = input_action_button("btn", "Click me")

        assert isinstance(result, Tag)
        assert result.name == "button"
        result_str = str(result)
        assert "Click me" in result_str
        assert "btn" in result_str

    def test_action_button_has_action_button_class(self):
        """Test action button has action-button class."""
        result = input_action_button("btn", "Click")

        result_str = str(result)
        assert "action-button" in result_str

    def test_action_button_with_icon(self):
        """Test action button with icon."""
        icon = tags.i(class_="fa fa-play")
        result = input_action_button("btn", "Play", icon=icon)

        result_str = str(result)
        assert "fa-play" in result_str
        assert "action-icon" in result_str

    def test_action_button_with_width(self):
        """Test action button with custom width."""
        result = input_action_button("btn", "Click", width="200px")

        result_str = str(result)
        assert "200px" in result_str

    def test_action_button_disabled(self):
        """Test disabled action button."""
        result = input_action_button("btn", "Click", disabled=True)

        result_str = str(result)
        assert "disabled" in result_str

    def test_action_button_not_disabled(self):
        """Test non-disabled action button (default)."""
        result = input_action_button("btn", "Click", disabled=False)

        result_str = str(result)
        # Should not have explicit disabled attribute
        assert 'disabled=""' not in result_str

    def test_action_button_type_is_button(self):
        """Test that type attribute is 'button'."""
        result = input_action_button("btn", "Click")

        assert result.attrs.get("type") == "button"

    def test_action_button_has_btn_class(self):
        """Test action button has Bootstrap btn class."""
        result = input_action_button("btn", "Click")

        result_str = str(result)
        assert "btn" in result_str
        assert "btn-default" in result_str

    def test_action_button_with_custom_class(self):
        """Test action button with additional class."""
        result = input_action_button("btn", "Click", class_="btn-primary")

        result_str = str(result)
        assert "btn-primary" in result_str

    def test_action_button_none_label(self):
        """Test action button with None label."""
        result = input_action_button("btn", None)

        # Should still create button
        assert isinstance(result, Tag)
        assert result.name == "button"

    def test_action_button_none_icon(self):
        """Test action button with None icon (default)."""
        result = input_action_button("btn", "Click", icon=None)

        result_str = str(result)
        assert "action-icon" not in result_str

    def test_action_button_with_kwargs(self):
        """Test action button with additional kwargs."""
        result = input_action_button("btn", "Click", data_custom="value")

        result_str = str(result)
        assert "data-custom" in result_str


class TestInputActionLink:
    """Tests for the input_action_link function."""

    def test_action_link_basic(self):
        """Test basic action link creation."""
        result = input_action_link("link", "Click me")

        assert isinstance(result, Tag)
        assert result.name == "a"
        result_str = str(result)
        assert "Click me" in result_str

    def test_action_link_has_action_button_class(self):
        """Test action link has action-button class."""
        result = input_action_link("link", "Click")

        result_str = str(result)
        assert "action-button" in result_str
        assert "action-link" in result_str

    def test_action_link_with_icon(self):
        """Test action link with icon."""
        icon = tags.i(class_="fa fa-info")
        result = input_action_link("link", "Info", icon=icon)

        result_str = str(result)
        assert "fa-info" in result_str
        assert "action-icon" in result_str

    def test_action_link_href_is_hash(self):
        """Test action link has href='#'."""
        result = input_action_link("link", "Click")

        assert result.attrs.get("href") == "#"

    def test_action_link_with_custom_class(self):
        """Test action link with additional class."""
        result = input_action_link("link", "Click", class_="custom-link")

        result_str = str(result)
        assert "custom-link" in result_str

    def test_action_link_none_label(self):
        """Test action link with None label."""
        result = input_action_link("link", None)

        # Should still create link
        assert isinstance(result, Tag)
        assert result.name == "a"

    def test_action_link_none_icon(self):
        """Test action link with None icon (default)."""
        result = input_action_link("link", "Click", icon=None)

        result_str = str(result)
        assert "action-icon" not in result_str

    def test_action_link_with_kwargs(self):
        """Test action link with additional kwargs."""
        result = input_action_link("link", "Click", data_custom="value")

        result_str = str(result)
        assert "data-custom" in result_str
