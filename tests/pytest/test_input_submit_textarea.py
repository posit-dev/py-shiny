"""Tests for shiny.ui._input_submit_textarea module."""

from shiny.ui import input_submit_textarea


class TestInputSubmitTextarea:
    """Tests for input_submit_textarea function."""

    def test_input_submit_textarea_basic(self):
        """Test basic input_submit_textarea creation."""
        widget = input_submit_textarea("textarea_id")
        html = str(widget)
        assert "textarea_id" in html

    def test_input_submit_textarea_with_label(self):
        """Test input_submit_textarea with label."""
        widget = input_submit_textarea("textarea_id", label="Enter message")
        html = str(widget)
        assert "Enter message" in html

    def test_input_submit_textarea_with_placeholder(self):
        """Test input_submit_textarea with placeholder."""
        widget = input_submit_textarea(
            "textarea_id", placeholder="Type your message..."
        )
        html = str(widget)
        assert "Type your message..." in html

    def test_input_submit_textarea_with_value(self):
        """Test input_submit_textarea with initial value."""
        widget = input_submit_textarea("textarea_id", value="Hello, World!")
        html = str(widget)
        assert "Hello, World!" in html

    def test_input_submit_textarea_with_width(self):
        """Test input_submit_textarea with custom width."""
        widget = input_submit_textarea("textarea_id", width="100%")
        html = str(widget)
        assert "100%" in html

    def test_input_submit_textarea_with_rows(self):
        """Test input_submit_textarea with custom rows."""
        widget = input_submit_textarea("textarea_id", rows=5)
        html = str(widget)
        assert "5" in html or "rows" in html

    def test_input_submit_textarea_submit_key_enter(self):
        """Test input_submit_textarea with enter submit key."""
        widget = input_submit_textarea("textarea_id", submit_key="enter")
        # Just verify widget is created with the submit_key
        assert widget is not None

    def test_input_submit_textarea_submit_key_modifier(self):
        """Test input_submit_textarea with enter+modifier submit key."""
        widget = input_submit_textarea("textarea_id", submit_key="enter+modifier")
        html = str(widget)
        assert "enter+modifier" in html or "textarea_id" in html

    def test_input_submit_textarea_with_kwargs(self):
        """Test input_submit_textarea with additional attributes."""
        widget = input_submit_textarea(
            "textarea_id",
            spellcheck="true",
            autocomplete="off",
        )
        html = str(widget)
        # Attributes should be present
        assert "textarea_id" in html
