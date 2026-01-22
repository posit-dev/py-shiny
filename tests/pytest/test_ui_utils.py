"""Tests for shiny/ui/_utils.py"""

from __future__ import annotations

import os
from typing import Callable

from htmltools import Tag, TagList, tags

from shiny.types import MISSING
from shiny.ui._utils import (
    JSEval,
    _find_child_strings,
    _session_on_flush_send_msg,
    css_no_sub,
    extract_js_keys,
    get_window_title,
    is_01_scalar,
    js_eval,
    path_pkg_www,
    shiny_input_label,
)


class TestShinyInputLabel:
    """Tests for the shiny_input_label function."""

    def test_label_with_text(self) -> None:
        """Test label with text content."""
        result = shiny_input_label("my_id", "My Label")

        assert isinstance(result, Tag)
        assert result.name == "label"
        rendered = str(result)
        assert 'id="my_id-label"' in rendered
        assert 'for="my_id"' in rendered
        assert "My Label" in rendered
        assert "control-label" in rendered

    def test_label_without_label_content(self) -> None:
        """Test label without label content (None)."""
        result = shiny_input_label("my_id", None)

        rendered = str(result)
        assert "shiny-label-null" in rendered

    def test_label_with_html_content(self) -> None:
        """Test label with HTML content."""
        result = shiny_input_label("my_id", tags.strong("Bold Label"))

        rendered = str(result)
        assert "<strong>Bold Label</strong>" in rendered


class TestGetWindowTitle:
    """Tests for the get_window_title function."""

    def test_none_title_with_missing_window_title(self) -> None:
        """Test None title with MISSING window_title returns None."""
        result = get_window_title(None, MISSING)
        assert result is None

    def test_none_title_with_window_title(self) -> None:
        """Test None title with explicit window_title."""
        result = get_window_title(None, "My Window Title")

        assert result is not None
        # Should create an HTMLDependency with a title tag

    def test_string_title_extracts_window_title(self) -> None:
        """Test string title extracts window_title."""
        result = get_window_title("Page Title", MISSING)

        assert result is not None

    def test_explicit_window_title_overrides(self) -> None:
        """Test explicit window_title is used."""
        result = get_window_title("Page Title", "Custom Window Title")

        assert result is not None


class TestFindChildStrings:
    """Tests for the _find_child_strings function."""

    def test_simple_string(self) -> None:
        """Test with simple string."""
        result = _find_child_strings("Hello")
        assert result == "Hello"

    def test_tag_with_text(self) -> None:
        """Test with tag containing text."""
        result = _find_child_strings(tags.div("Hello World"))
        assert result == "Hello World"

    def test_nested_tags(self) -> None:
        """Test with nested tags."""
        result = _find_child_strings(
            tags.div(tags.span("First"), " ", tags.span("Second"))
        )
        assert "First" in result
        assert "Second" in result

    def test_script_tag_ignored(self) -> None:
        """Test that script tags are ignored."""
        result = _find_child_strings(tags.script("console.log('test')"))
        assert result == ""

    def test_style_tag_ignored(self) -> None:
        """Test that style tags are ignored."""
        result = _find_child_strings(tags.style(".class { color: red; }"))
        assert result == ""

    def test_taglist(self) -> None:
        """Test with TagList."""
        result = _find_child_strings(TagList("First", " ", "Second"))
        assert "First" in result
        assert "Second" in result

    def test_empty_tag(self) -> None:
        """Test with empty tag."""
        result = _find_child_strings(tags.div())
        assert result == ""


class TestIs01Scalar:
    """Tests for the is_01_scalar function."""

    def test_zero(self) -> None:
        """Test that 0 is a valid 0-1 scalar."""
        assert is_01_scalar(0) is True
        assert is_01_scalar(0.0) is True

    def test_one(self) -> None:
        """Test that 1 is a valid 0-1 scalar."""
        assert is_01_scalar(1) is True
        assert is_01_scalar(1.0) is True

    def test_mid_values(self) -> None:
        """Test mid-range values."""
        assert is_01_scalar(0.5) is True
        assert is_01_scalar(0.25) is True
        assert is_01_scalar(0.75) is True

    def test_negative_fails(self) -> None:
        """Test that negative values fail."""
        assert is_01_scalar(-0.1) is False
        assert is_01_scalar(-1) is False

    def test_greater_than_one_fails(self) -> None:
        """Test that values > 1 fail."""
        assert is_01_scalar(1.1) is False
        assert is_01_scalar(2) is False

    def test_non_numeric_fails(self) -> None:
        """Test that non-numeric values fail."""
        assert is_01_scalar("0.5") is False
        assert is_01_scalar(None) is False
        assert is_01_scalar([0.5]) is False


class TestCssNoSub:
    """Tests for the css_no_sub function."""

    def test_single_property(self) -> None:
        """Test with single CSS property."""
        result = css_no_sub(color="red")
        assert result == "color:red;"

    def test_multiple_properties(self) -> None:
        """Test with multiple CSS properties."""
        result = css_no_sub(color="red", width="100px")
        assert result is not None
        assert "color:red;" in result
        assert "width:100px;" in result

    def test_none_value_skipped(self) -> None:
        """Test that None values are skipped."""
        result = css_no_sub(color=None, width="100px")
        assert result == "width:100px;"

    def test_all_none_returns_none(self) -> None:
        """Test that all None values return None."""
        result = css_no_sub(color=None, width=None)
        assert result is None

    def test_empty_returns_none(self) -> None:
        """Test that no properties returns None."""
        result = css_no_sub()
        assert result is None

    def test_numeric_value(self) -> None:
        """Test with numeric values."""
        result = css_no_sub(opacity=0.5)
        assert result == "opacity:0.5;"


class TestJSEval:
    """Tests for the JSEval class and js_eval function."""

    def test_jseval_is_string(self) -> None:
        """Test that JSEval is a string subclass."""
        js = JSEval("function() { return 1; }")
        assert isinstance(js, str)
        assert js == "function() { return 1; }"

    def test_js_eval_creates_jseval(self) -> None:
        """Test that js_eval creates a JSEval instance."""
        result = js_eval("function() { return 1; }")
        assert isinstance(result, JSEval)
        assert result == "function() { return 1; }"


class TestExtractJsKeys:
    """Tests for the extract_js_keys function."""

    def test_empty_dict(self) -> None:
        """Test with empty dictionary."""
        result = extract_js_keys({})
        assert result == []

    def test_no_js_values(self) -> None:
        """Test with dictionary containing no JSEval values."""
        result = extract_js_keys({"a": 1, "b": "string"})
        assert result == []

    def test_single_js_value(self) -> None:
        """Test with single JSEval value."""
        result = extract_js_keys({"callback": JSEval("function() {}")})
        assert result == ["callback"]

    def test_multiple_js_values(self) -> None:
        """Test with multiple JSEval values."""
        result = extract_js_keys(
            {
                "a": 1,
                "onInit": JSEval("function() {}"),
                "onComplete": JSEval("function() {}"),
            }
        )
        assert "onInit" in result
        assert "onComplete" in result
        assert len(result) == 2

    def test_nested_js_values(self) -> None:
        """Test with nested JSEval values."""
        result = extract_js_keys(
            {"callbacks": {"onInit": JSEval("function() {}"), "regular": "value"}}
        )
        assert result == ["callbacks.onInit"]

    def test_deeply_nested_js_values(self) -> None:
        """Test with deeply nested JSEval values."""
        result = extract_js_keys(
            {"level1": {"level2": {"callback": JSEval("function() {}")}}}
        )
        assert result == ["level1.level2.callback"]


class TestPathPkgWww:
    """Tests for the path_pkg_www function."""

    def test_returns_path(self) -> None:
        """Test that it returns a path string."""
        result = path_pkg_www()
        assert isinstance(result, str)
        assert "www" in result
        assert "shared" in result

    def test_with_args(self) -> None:
        """Test with additional path arguments."""
        result = path_pkg_www("jquery")
        assert result.endswith("jquery")

    def test_multiple_args(self) -> None:
        """Test with multiple path arguments."""
        result = path_pkg_www("folder", "file.js")
        assert os.path.join("folder", "file.js") in result


class TestSessionOnFlushSendMsg:
    """Tests for the _session_on_flush_send_msg function."""

    def test_sends_message(self) -> None:
        """Test that it registers an on_flush callback that sends the message."""
        from unittest.mock import MagicMock

        mock_session = MagicMock()
        msg: dict[str, object] = {"action": "update"}

        # Capture the callback passed to on_flush
        on_flush_cb: Callable[[], None] | None = None

        def side_effect(fn: Callable[[], None], once: bool = False) -> None:
            nonlocal on_flush_cb
            on_flush_cb = fn

        mock_session.on_flush.side_effect = side_effect

        _session_on_flush_send_msg("my_id", mock_session, msg)

        assert mock_session.on_flush.called
        assert mock_session.on_flush.call_args[1]["once"] is True
        assert on_flush_cb is not None

        # Execute the callback
        on_flush_cb()
        mock_session.send_input_message.assert_called_with("my_id", msg)
