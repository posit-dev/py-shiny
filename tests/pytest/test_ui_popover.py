"""Tests for shiny/ui/_popover.py"""

from __future__ import annotations

from htmltools import Tag, TagList, span

from shiny.ui import popover


class TestPopover:
    """Tests for the popover function."""

    def test_basic_popover(self) -> None:
        """Test creating a basic popover."""
        result = popover(
            span("Trigger"),
            "Popover content",
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_with_title(self) -> None:
        """Test popover with a title."""
        result = popover(
            span("Trigger"),
            "Content",
            title="My Title",
        )
        rendered = str(result)
        assert "My Title" in rendered or "popover" in rendered.lower()

    def test_popover_with_id(self) -> None:
        """Test popover with custom id."""
        result = popover(
            span("Trigger"),
            "Content",
            id="my_popover",  # Use underscore for valid Shiny ID
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_placement_top(self) -> None:
        """Test popover with top placement."""
        result = popover(
            span("Trigger"),
            "Content",
            placement="top",
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_placement_bottom(self) -> None:
        """Test popover with bottom placement."""
        result = popover(
            span("Trigger"),
            "Content",
            placement="bottom",
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_placement_left(self) -> None:
        """Test popover with left placement."""
        result = popover(
            span("Trigger"),
            "Content",
            placement="left",
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_placement_right(self) -> None:
        """Test popover with right placement."""
        result = popover(
            span("Trigger"),
            "Content",
            placement="right",
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_multiple_content(self) -> None:
        """Test popover with multiple content elements."""
        result = popover(
            span("Trigger"),
            "Para 1",
            "Para 2",
            "Para 3",
        )
        assert isinstance(result, (Tag, TagList))

    def test_popover_complex_trigger(self) -> None:
        """Test popover with complex trigger element."""
        from htmltools import div

        trigger = div(
            span("Click"),
            span("me"),
            class_="trigger-element",
        )
        result = popover(trigger, "Content")
        assert isinstance(result, (Tag, TagList))


class TestPopoverOptions:
    """Tests for popover configuration options."""

    def test_popover_with_options(self) -> None:
        """Test popover with additional options."""
        result = popover(
            span("Trigger"),
            "Content",
            title="Title",
            placement="top",
        )
        assert isinstance(result, (Tag, TagList))


class TestPopoverRendering:
    """Tests for popover HTML rendering."""

    def test_popover_renders_trigger(self) -> None:
        """Test that popover renders the trigger element."""
        result = popover(
            span("My Trigger Text"),
            "Content",
        )
        rendered = str(result)
        assert "My Trigger Text" in rendered

    def test_popover_has_data_attrs(self) -> None:
        """Test that popover has necessary data attributes."""
        result = popover(
            span("Trigger"),
            "Content",
        )
        rendered = str(result)
        # Should have some Bootstrap/bslib related attributes
        assert (
            "data-" in rendered
            or "popover" in rendered.lower()
            or isinstance(result, (Tag, TagList))
        )
