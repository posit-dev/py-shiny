"""Tests for shiny.ui._popover module."""

from htmltools import Tag, div

from shiny.ui._popover import popover


class TestPopover:
    """Tests for popover function."""

    def test_popover_basic(self) -> None:
        """Test basic popover creation."""
        result = popover(div("Click me"), "Popover content")
        assert isinstance(result, Tag)

    def test_popover_with_trigger(self) -> None:
        """Test popover with trigger element."""
        result = popover(div("Trigger"), "Content")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_content(self) -> None:
        """Test popover with content."""
        result = popover(div("Trigger"), "Popover body text")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_title(self) -> None:
        """Test popover with title."""
        result = popover(div("Trigger"), "Content", title="Popover Title")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_placement_top(self) -> None:
        """Test popover with placement='top'."""
        result = popover(div("Trigger"), "Content", placement="top")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_placement_bottom(self) -> None:
        """Test popover with placement='bottom'."""
        result = popover(div("Trigger"), "Content", placement="bottom")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_placement_left(self) -> None:
        """Test popover with placement='left'."""
        result = popover(div("Trigger"), "Content", placement="left")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_placement_right(self) -> None:
        """Test popover with placement='right'."""
        result = popover(div("Trigger"), "Content", placement="right")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_id(self) -> None:
        """Test popover with id parameter."""
        result = popover(div("Trigger"), "Content", id="my_popover")
        html = str(result)
        assert "Trigger" in html

    def test_popover_with_options(self) -> None:
        """Test popover with options dict."""
        result = popover(div("Trigger"), "Content", options={"trigger": "focus"})
        html = str(result)
        assert "Trigger" in html
