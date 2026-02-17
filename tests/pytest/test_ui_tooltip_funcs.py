"""Tests for shiny/ui/_tooltip.py module."""

from shiny.ui._tooltip import (
    tooltip,
)


class TestTooltip:
    """Tests for tooltip function."""

    def test_tooltip_is_callable(self):
        """Test tooltip is callable."""
        assert callable(tooltip)


class TestTooltipExported:
    """Tests for tooltip functions export."""

    def test_tooltip_in_ui(self):
        """Test tooltip is in ui module."""
        from shiny import ui

        assert hasattr(ui, "tooltip")

    def test_update_tooltip_in_ui(self):
        """Test update_tooltip is in ui module."""
        from shiny import ui

        assert hasattr(ui, "update_tooltip")
