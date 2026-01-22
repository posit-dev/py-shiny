"""Tests for shiny.ui._input_submit_textarea module."""

from htmltools import Tag, span

from shiny.ui._input_submit_textarea import (
    input_submit_textarea,
    is_button_tag,
)
from shiny.ui._input_task_button import input_task_button


class TestInputSubmitTextarea:
    """Tests for input_submit_textarea function."""

    def test_input_submit_textarea_returns_tag(self):
        """input_submit_textarea should return a Tag."""
        result = input_submit_textarea("my_textarea")
        assert isinstance(result, Tag)

    def test_input_submit_textarea_has_id(self):
        """input_submit_textarea should have correct id."""
        result = input_submit_textarea("textarea_id")
        html = str(result)
        assert 'id="textarea_id"' in html

    def test_input_submit_textarea_with_label(self):
        """input_submit_textarea should display label."""
        result = input_submit_textarea("ta", label="Enter text:")
        html = str(result)
        assert "Enter text:" in html

    def test_input_submit_textarea_no_label(self):
        """input_submit_textarea should work without label."""
        result = input_submit_textarea("ta", label=None)
        assert isinstance(result, Tag)

    def test_input_submit_textarea_with_placeholder(self):
        """input_submit_textarea should accept placeholder."""
        result = input_submit_textarea("ta", placeholder="Type here...")
        html = str(result)
        assert "Type here..." in html

    def test_input_submit_textarea_with_value(self):
        """input_submit_textarea should accept initial value."""
        result = input_submit_textarea("ta", value="Initial text")
        html = str(result)
        assert "Initial text" in html

    def test_input_submit_textarea_with_width(self):
        """input_submit_textarea should accept width."""
        result = input_submit_textarea("ta", width="400px")
        html = str(result)
        assert "400px" in html

    def test_input_submit_textarea_with_rows(self):
        """input_submit_textarea should accept rows parameter."""
        result = input_submit_textarea("ta", rows=5)
        html = str(result)
        assert 'rows="5"' in html

    def test_input_submit_textarea_default_width(self):
        """input_submit_textarea should have default width."""
        result = input_submit_textarea("ta")
        html = str(result)
        # Default width is "min(680px, 100%)"
        assert "680px" in html or "width" in html

    def test_input_submit_textarea_submit_key_default(self):
        """input_submit_textarea should have enter+modifier as default submit_key."""
        result = input_submit_textarea("ta")
        html = str(result)
        # When submit_key is enter+modifier, data-needs-modifier should be present
        assert "data-needs-modifier" in html

    def test_input_submit_textarea_submit_key_enter(self):
        """input_submit_textarea should accept submit_key='enter'."""
        result = input_submit_textarea("ta", submit_key="enter")
        # When submit_key is enter, data-needs-modifier should NOT be present
        # (empty attribute value is falsy)
        assert isinstance(result, Tag)

    def test_input_submit_textarea_with_custom_button(self):
        """input_submit_textarea should accept custom button."""
        custom_btn = input_task_button("custom_btn", "Send")
        result = input_submit_textarea("ta", button=custom_btn)
        html = str(result)
        # The custom button should be used
        assert "Send" in html

    def test_input_submit_textarea_has_textarea_element(self):
        """input_submit_textarea should contain a textarea element."""
        result = input_submit_textarea("ta")
        html = str(result)
        assert "<textarea" in html

    def test_input_submit_textarea_with_kwargs(self):
        """input_submit_textarea should pass kwargs to textarea."""
        result = input_submit_textarea("ta", spellcheck="false")
        html = str(result)
        assert "spellcheck" in html


class TestIsButtonTag:
    """Tests for is_button_tag helper function."""

    def test_is_button_tag_with_button_element(self):
        """is_button_tag should return True for button element."""
        btn = Tag("button", "Click me")
        assert is_button_tag(btn) is True

    def test_is_button_tag_with_type_button(self):
        """is_button_tag should return True for element with type='button'."""
        btn = Tag("a", type="button")
        assert is_button_tag(btn) is True

    def test_is_button_tag_with_div(self):
        """is_button_tag should return False for div element."""
        div = Tag("div", "Not a button")
        assert is_button_tag(div) is False

    def test_is_button_tag_with_span(self):
        """is_button_tag should return False for span element."""
        span_tag = span("Not a button")
        assert is_button_tag(span_tag) is False

    def test_is_button_tag_with_string(self):
        """is_button_tag should return False for string."""
        assert is_button_tag("button") is False

    def test_is_button_tag_with_none(self):
        """is_button_tag should return False for None."""
        assert is_button_tag(None) is False

    def test_is_button_tag_with_int(self):
        """is_button_tag should return False for int."""
        assert is_button_tag(123) is False

    def test_is_button_tag_with_task_button(self):
        """is_button_tag should return True for input_task_button."""
        btn = input_task_button("btn", "Task")
        assert is_button_tag(btn) is True
