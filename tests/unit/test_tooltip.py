"""Unit tests for shiny.ui._tooltip module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import tooltip


class TestTooltip:
    """Tests for tooltip function."""

    def test_basic_tooltip(self) -> None:
        """Test basic tooltip with trigger and content."""
        trigger = tags.button("Click me", type="button")
        result = tooltip(trigger, "Tooltip content")
        html = str(result)

        assert "Click me" in html
        assert "Tooltip content" in html

    def test_tooltip_returns_tag(self) -> None:
        """Test that tooltip returns a Tag."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content")
        assert isinstance(result, Tag)

    def test_tooltip_with_id(self) -> None:
        """Test tooltip with id parameter."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", id="my_tooltip")
        html = str(result)

        assert "my_tooltip" in html

    def test_tooltip_placement_top(self) -> None:
        """Test tooltip with placement='top'."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", placement="top")
        html = str(result)

        assert "top" in html

    def test_tooltip_placement_bottom(self) -> None:
        """Test tooltip with placement='bottom'."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", placement="bottom")
        html = str(result)

        assert "bottom" in html

    def test_tooltip_placement_left(self) -> None:
        """Test tooltip with placement='left'."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", placement="left")
        html = str(result)

        assert "left" in html

    def test_tooltip_placement_right(self) -> None:
        """Test tooltip with placement='right'."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", placement="right")
        html = str(result)

        assert "right" in html

    def test_tooltip_placement_auto(self) -> None:
        """Test tooltip with placement='auto' (default)."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", placement="auto")
        html = str(result)

        assert "auto" in html

    def test_tooltip_multiple_content(self) -> None:
        """Test tooltip with multiple content children."""
        trigger = tags.button("Click", type="button")
        result = tooltip(
            trigger,
            tags.span("First part"),
            tags.span("Second part"),
        )
        html = str(result)

        assert "First part" in html
        assert "Second part" in html

    def test_tooltip_with_options(self) -> None:
        """Test tooltip with custom options."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", options={"delay": 500})
        html = str(result)

        # Should include the trigger and content
        assert "Click" in html
        assert "Content" in html

    def test_tooltip_with_kwargs(self) -> None:
        """Test tooltip with custom kwargs."""
        trigger = tags.button("Click", type="button")
        result = tooltip(trigger, "Content", class_="custom-class")
        html = str(result)

        assert "custom-class" in html

    def test_tooltip_html_content(self) -> None:
        """Test tooltip with HTML content."""
        trigger = tags.button("Click", type="button")
        content = tags.strong("Bold content")
        result = tooltip(trigger, content)
        html = str(result)

        assert "<strong>Bold content</strong>" in html

    def test_tooltip_icon_trigger(self) -> None:
        """Test tooltip with icon as trigger."""
        trigger = tags.i(class_="fa fa-info-circle")
        result = tooltip(trigger, "Info content")
        html = str(result)

        assert "fa-info-circle" in html
        assert "Info content" in html

    def test_tooltip_link_trigger(self) -> None:
        """Test tooltip with link as trigger."""
        trigger = tags.a("Help", href="#")
        result = tooltip(trigger, "Help content")
        html = str(result)

        assert "Help" in html
        assert "Help content" in html

    def test_tooltip_span_trigger(self) -> None:
        """Test tooltip with span as trigger (non-interactive element)."""
        trigger = tags.span("Hover me")
        result = tooltip(trigger, "Hover content")
        html = str(result)

        assert "Hover me" in html
        assert "Hover content" in html
