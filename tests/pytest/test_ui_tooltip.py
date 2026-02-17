"""Tests for shiny/ui/_tooltip.py"""

from __future__ import annotations

import pytest
from htmltools import Tag

from shiny.ui._tooltip import tooltip


class TestTooltip:
    """Tests for tooltip function."""

    def test_tooltip_basic(self) -> None:
        """Test basic tooltip creation."""
        result = tooltip("Hover me", "Tooltip content")
        assert isinstance(result, Tag)
        html = str(result)
        assert "bslib-tooltip" in html
        assert "Hover me" in html

    def test_tooltip_with_id(self) -> None:
        """Test tooltip with id."""
        result = tooltip("Hover me", "Content", id="tip1")
        html = str(result)
        assert "tip1" in html

    def test_tooltip_placement_top(self) -> None:
        """Test tooltip with placement='top'."""
        result = tooltip("Hover", "Content", placement="top")
        html = str(result)
        assert 'placement="top"' in html

    def test_tooltip_placement_bottom(self) -> None:
        """Test tooltip with placement='bottom'."""
        result = tooltip("Hover", "Content", placement="bottom")
        html = str(result)
        assert 'placement="bottom"' in html

    def test_tooltip_placement_left(self) -> None:
        """Test tooltip with placement='left'."""
        result = tooltip("Hover", "Content", placement="left")
        html = str(result)
        assert 'placement="left"' in html

    def test_tooltip_placement_right(self) -> None:
        """Test tooltip with placement='right'."""
        result = tooltip("Hover", "Content", placement="right")
        html = str(result)
        assert 'placement="right"' in html

    def test_tooltip_with_options(self) -> None:
        """Test tooltip with custom options."""
        result = tooltip("Hover", "Content", options={"delay": 100})
        html = str(result)
        assert "bsOptions" in html

    def test_tooltip_no_content_raises(self) -> None:
        """Test that tooltip raises error with no content."""
        with pytest.raises(RuntimeError):
            tooltip("Hover")

    def test_tooltip_multiple_content(self) -> None:
        """Test tooltip with multiple content items."""
        result = tooltip("Hover", "Line 1", "Line 2", "Line 3")
        html = str(result)
        assert "Line 1" in html
        assert "Line 2" in html
        assert "Line 3" in html
