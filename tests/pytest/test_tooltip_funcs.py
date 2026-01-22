"""Tests for shiny.ui._tooltip module."""

from htmltools import Tag, div

from shiny.ui._tooltip import tooltip


class TestTooltip:
    """Tests for tooltip function."""

    def test_tooltip_basic(self) -> None:
        """Test basic tooltip creation."""
        result = tooltip(div("Trigger"), "Tooltip text")
        assert isinstance(result, Tag)

    def test_tooltip_with_trigger(self) -> None:
        """Test tooltip with trigger element."""
        result = tooltip(div("Hover me"), "Tooltip content")
        html = str(result)
        assert "Hover me" in html

    def test_tooltip_with_text(self) -> None:
        """Test tooltip with text content."""
        result = tooltip(div("Trigger"), "This is a tooltip")
        html = str(result)
        assert "Trigger" in html

    def test_tooltip_with_placement_top(self) -> None:
        """Test tooltip with placement='top'."""
        result = tooltip(div("Trigger"), "Text", placement="top")
        html = str(result)
        assert "Trigger" in html

    def test_tooltip_with_placement_bottom(self) -> None:
        """Test tooltip with placement='bottom'."""
        result = tooltip(div("Trigger"), "Text", placement="bottom")
        html = str(result)
        assert "Trigger" in html

    def test_tooltip_with_placement_left(self) -> None:
        """Test tooltip with placement='left'."""
        result = tooltip(div("Trigger"), "Text", placement="left")
        html = str(result)
        assert "Trigger" in html

    def test_tooltip_with_placement_right(self) -> None:
        """Test tooltip with placement='right'."""
        result = tooltip(div("Trigger"), "Text", placement="right")
        html = str(result)
        assert "Trigger" in html

    def test_tooltip_with_id(self) -> None:
        """Test tooltip with id parameter."""
        result = tooltip(div("Trigger"), "Text", id="my_tooltip")
        html = str(result)
        assert "Trigger" in html

    def test_tooltip_with_options(self) -> None:
        """Test tooltip with options dict."""
        result = tooltip(div("Trigger"), "Text", options={"delay": 500})
        html = str(result)
        assert "Trigger" in html
