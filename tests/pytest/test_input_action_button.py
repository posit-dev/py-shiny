"""Tests for shiny/ui/_input_action_button.py - Action button and link inputs."""

from shiny.ui._input_action_button import input_action_button, input_action_link


class TestInputActionButton:
    """Tests for input_action_button function."""

    def test_input_action_button_basic(self):
        """Test basic input_action_button."""
        btn = input_action_button("my_btn", "Click Me")
        html = str(btn)
        assert 'id="my_btn"' in html
        assert "Click Me" in html
        assert "btn btn-default action-button" in html
        assert 'type="button"' in html

    def test_input_action_button_with_icon(self):
        """Test input_action_button with icon."""
        from htmltools import tags

        icon = tags.i(class_="bi bi-check")
        btn = input_action_button("my_btn", "Click", icon=icon)
        html = str(btn)
        assert "action-icon" in html
        assert "bi bi-check" in html

    def test_input_action_button_with_width(self):
        """Test input_action_button with custom width."""
        btn = input_action_button("my_btn", "Click", width="200px")
        html = str(btn)
        assert "width:200px" in html

    def test_input_action_button_disabled(self):
        """Test input_action_button disabled state."""
        btn = input_action_button("my_btn", "Click", disabled=True)
        html = str(btn)
        assert 'disabled=""' in html

    def test_input_action_button_not_disabled(self):
        """Test input_action_button not disabled by default."""
        btn = input_action_button("my_btn", "Click")
        html = str(btn)
        assert "disabled" not in html

    def test_input_action_button_with_kwargs(self):
        """Test input_action_button with additional kwargs."""
        btn = input_action_button("my_btn", "Click", data_custom="value")
        html = str(btn)
        assert 'data-custom="value"' in html

    def test_input_action_button_label_wrapped(self):
        """Test input_action_button wraps label in span."""
        btn = input_action_button("my_btn", "My Label")
        html = str(btn)
        assert "action-label" in html


class TestInputActionLink:
    """Tests for input_action_link function."""

    def test_input_action_link_basic(self):
        """Test basic input_action_link."""
        link = input_action_link("my_link", "Click Here")
        html = str(link)
        assert 'id="my_link"' in html
        assert "Click Here" in html
        assert "action-button action-link" in html
        assert 'href="#"' in html
        assert "<a" in html

    def test_input_action_link_with_icon(self):
        """Test input_action_link with icon."""
        from htmltools import tags

        icon = tags.i(class_="bi bi-arrow-right")
        link = input_action_link("my_link", "Click", icon=icon)
        html = str(link)
        assert "action-icon" in html
        assert "bi bi-arrow-right" in html

    def test_input_action_link_with_kwargs(self):
        """Test input_action_link with additional kwargs."""
        link = input_action_link("my_link", "Click", target="_blank")
        html = str(link)
        assert 'target="_blank"' in html

    def test_input_action_link_label_wrapped(self):
        """Test input_action_link wraps label in span."""
        link = input_action_link("my_link", "My Label")
        html = str(link)
        assert "action-label" in html
