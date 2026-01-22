"""Tests for shiny/ui/_popover.py"""

from __future__ import annotations

import pytest
from htmltools import Tag

from shiny.ui._popover import popover


class TestPopover:
    """Tests for popover function."""

    def test_popover_basic(self) -> None:
        """Test basic popover creation."""
        result = popover("Click me", "Popover content")
        assert isinstance(result, Tag)
        html = str(result)
        assert "bslib-popover" in html
        assert "Click me" in html

    def test_popover_with_title(self) -> None:
        """Test popover with title."""
        result = popover("Click", "Content", title="Title")
        html = str(result)
        assert "Title" in html

    def test_popover_with_id(self) -> None:
        """Test popover with id."""
        result = popover("Click", "Content", id="pop1")
        html = str(result)
        assert "pop1" in html

    def test_popover_placement_top(self) -> None:
        """Test popover with placement='top'."""
        result = popover("Click", "Content", placement="top")
        html = str(result)
        assert 'placement="top"' in html

    def test_popover_placement_bottom(self) -> None:
        """Test popover with placement='bottom'."""
        result = popover("Click", "Content", placement="bottom")
        html = str(result)
        assert 'placement="bottom"' in html

    def test_popover_placement_left(self) -> None:
        """Test popover with placement='left'."""
        result = popover("Click", "Content", placement="left")
        html = str(result)
        assert 'placement="left"' in html

    def test_popover_placement_right(self) -> None:
        """Test popover with placement='right'."""
        result = popover("Click", "Content", placement="right")
        html = str(result)
        assert 'placement="right"' in html

    def test_popover_with_options(self) -> None:
        """Test popover with custom options."""
        result = popover("Click", "Content", options={"trigger": "hover"})
        html = str(result)
        assert "bsOptions" in html

    def test_popover_no_content_raises(self) -> None:
        """Test that popover raises error with no content."""
        with pytest.raises(RuntimeError):
            popover("Click")

    def test_popover_reserved_option_content_raises(self) -> None:
        """Test that reserved option 'content' raises error."""
        with pytest.raises(RuntimeError):
            popover("Click", "Content", options={"content": "invalid"})

    def test_popover_reserved_option_title_raises(self) -> None:
        """Test that reserved option 'title' raises error."""
        with pytest.raises(RuntimeError):
            popover("Click", "Content", options={"title": "invalid"})

    def test_popover_reserved_option_placement_raises(self) -> None:
        """Test that reserved option 'placement' raises error."""
        with pytest.raises(RuntimeError):
            popover("Click", "Content", options={"placement": "invalid"})

    def test_popover_multiple_content(self) -> None:
        """Test popover with multiple content items."""
        result = popover("Click", "Item 1", "Item 2", "Item 3")
        html = str(result)
        assert "Item 1" in html
        assert "Item 2" in html
        assert "Item 3" in html
