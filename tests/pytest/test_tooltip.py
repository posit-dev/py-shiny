"""Tests for shiny/ui/_tooltip.py module."""

from shiny.ui._tooltip import tooltip


class TestTooltip:
    """Tests for tooltip function."""

    def test_tooltip_is_callable(self):
        """Test tooltip is callable."""
        assert callable(tooltip)

    def test_tooltip_returns_tag(self):
        """Test tooltip returns a Tag."""
        from htmltools import Tag

        trigger = Tag("span", "hover me")
        result = tooltip(trigger, "Tooltip text")
        assert isinstance(result, Tag)

    def test_tooltip_with_placement(self):
        """Test tooltip with placement parameter."""
        from htmltools import Tag

        trigger = Tag("span", "hover me")
        result = tooltip(trigger, "Tooltip text", placement="bottom")
        assert isinstance(result, Tag)

    def test_tooltip_with_id(self):
        """Test tooltip with id parameter."""
        from htmltools import Tag

        trigger = Tag("span", "hover me")
        result = tooltip(trigger, "Tooltip text", id="my_tooltip")
        assert isinstance(result, Tag)


class TestTooltipExported:
    """Tests for tooltip export."""

    def test_tooltip_in_ui(self):
        """Test tooltip is in ui module."""
        from shiny import ui

        assert hasattr(ui, "tooltip")
