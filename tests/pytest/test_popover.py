"""Tests for shiny/ui/_popover.py module."""

from shiny.ui._popover import popover


class TestPopover:
    """Tests for popover function."""

    def test_popover_is_callable(self):
        """Test popover is callable."""
        assert callable(popover)

    def test_popover_returns_tag(self):
        """Test popover returns a Tag."""
        from htmltools import Tag

        trigger = Tag("span", "click me")
        result = popover(trigger, "Popover content")
        assert isinstance(result, Tag)

    def test_popover_with_title(self):
        """Test popover with title parameter."""
        from htmltools import Tag

        trigger = Tag("span", "click me")
        result = popover(trigger, "Content", title="My Title")
        assert isinstance(result, Tag)

    def test_popover_with_placement(self):
        """Test popover with placement parameter."""
        from htmltools import Tag

        trigger = Tag("span", "click me")
        result = popover(trigger, "Content", placement="bottom")
        assert isinstance(result, Tag)

    def test_popover_with_id(self):
        """Test popover with id parameter."""
        from htmltools import Tag

        trigger = Tag("span", "click me")
        result = popover(trigger, "Content", id="my_popover")
        assert isinstance(result, Tag)


class TestPopoverExported:
    """Tests for popover export."""

    def test_popover_in_ui(self):
        """Test popover is in ui module."""
        from shiny import ui

        assert hasattr(ui, "popover")
