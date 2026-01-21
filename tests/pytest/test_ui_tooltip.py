"""Tests for shiny/ui/_tooltip.py"""

from __future__ import annotations

import pytest
from htmltools import Tag, tags

from shiny.ui._tooltip import tooltip


class TestTooltip:
    """Tests for the tooltip function."""

    def test_basic_tooltip(self) -> None:
        """Test basic tooltip creation."""
        result = tooltip(tags.button("Click me"), "This is a tooltip")

        assert isinstance(result, Tag)
        assert result.name == "bslib-tooltip"

    def test_tooltip_with_id(self) -> None:
        """Test tooltip with id."""
        result = tooltip(tags.button("Click me"), "Tooltip text", id="my_tooltip")

        rendered = str(result)
        assert 'id="my_tooltip"' in rendered

    def test_tooltip_placement_options(self) -> None:
        """Test different placement options."""
        placements = ["auto", "top", "right", "bottom", "left"]

        for placement in placements:
            result = tooltip(
                tags.span("Trigger"), "Tooltip", placement=placement  # type: ignore
            )
            rendered = str(result)
            assert f'placement="{placement}"' in rendered

    def test_tooltip_no_content_raises(self) -> None:
        """Test that tooltip without content raises error."""
        with pytest.raises(RuntimeError, match="At least one value must be provided"):
            tooltip(tags.button("Trigger"))

    def test_tooltip_with_options(self) -> None:
        """Test tooltip with custom Bootstrap options."""
        result = tooltip(
            tags.button("Trigger"),
            "Tooltip text",
            options={"trigger": "click", "delay": 100},
        )

        rendered = str(result)
        # Options should be JSON-encoded
        assert "bsOptions" in rendered

    def test_tooltip_with_multiple_content_children(self) -> None:
        """Test tooltip with multiple content children."""
        result = tooltip(tags.button("Trigger"), "First line", tags.br(), "Second line")

        assert isinstance(result, Tag)
        rendered = str(result)
        assert "First line" in rendered
        assert "Second line" in rendered

    def test_tooltip_with_html_trigger(self) -> None:
        """Test tooltip with HTML trigger."""
        result = tooltip(tags.a("Link", href="#"), "Link tooltip")

        rendered = str(result)
        assert "Link" in rendered
        assert "Link tooltip" in rendered

    def test_tooltip_with_tag_attributes(self) -> None:
        """Test tooltip with additional tag attributes."""
        result = tooltip(tags.button("Trigger"), "Tooltip", class_="my-tooltip-class")

        rendered = str(result)
        assert "my-tooltip-class" in rendered

    def test_tooltip_default_placement(self) -> None:
        """Test that default placement is 'auto'."""
        result = tooltip(tags.button("Trigger"), "Tooltip")

        rendered = str(result)
        assert 'placement="auto"' in rendered


class TestTooltipRendering:
    """Tests for tooltip HTML rendering."""

    def test_tooltip_contains_trigger(self) -> None:
        """Test that tooltip contains the trigger element."""
        result = tooltip(tags.button("My Button", id="btn1"), "Tooltip text")

        rendered = str(result)
        assert "My Button" in rendered
        assert 'id="btn1"' in rendered

    def test_tooltip_contains_template(self) -> None:
        """Test that tooltip content is in a template tag."""
        result = tooltip(tags.span("Trigger"), "Content in template")

        rendered = str(result)
        assert "<template" in rendered

    def test_tooltip_structure(self) -> None:
        """Test the overall structure of the tooltip."""
        result = tooltip(
            tags.button("Trigger"), "Tooltip message", id="test_id", placement="top"
        )

        # Should be a bslib-tooltip web component
        assert result.name == "bslib-tooltip"

        # Check attributes
        rendered = str(result)
        assert 'id="test_id"' in rendered
        assert 'placement="top"' in rendered
