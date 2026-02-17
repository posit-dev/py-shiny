"""Unit tests for shiny.ui._popover module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import popover


class TestPopover:
    """Tests for popover function."""

    def test_basic_popover(self) -> None:
        """Test basic popover with trigger and content."""
        trigger = tags.button("Click me", type="button")
        result = popover(trigger, "Popover content")
        html = str(result)

        assert "Click me" in html
        assert "Popover content" in html

    def test_popover_returns_tag(self) -> None:
        """Test that popover returns a Tag."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content")
        assert isinstance(result, Tag)

    def test_popover_with_title(self) -> None:
        """Test popover with title parameter."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", title="My Title")
        html = str(result)

        assert "My Title" in html

    def test_popover_with_id(self) -> None:
        """Test popover with id parameter."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", id="my_popover")
        html = str(result)

        assert "my_popover" in html

    def test_popover_placement_top(self) -> None:
        """Test popover with placement='top'."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", placement="top")
        html = str(result)

        assert "top" in html

    def test_popover_placement_bottom(self) -> None:
        """Test popover with placement='bottom'."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", placement="bottom")
        html = str(result)

        assert "bottom" in html

    def test_popover_placement_left(self) -> None:
        """Test popover with placement='left'."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", placement="left")
        html = str(result)

        assert "left" in html

    def test_popover_placement_right(self) -> None:
        """Test popover with placement='right'."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", placement="right")
        html = str(result)

        assert "right" in html

    def test_popover_placement_auto(self) -> None:
        """Test popover with placement='auto' (default)."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", placement="auto")
        html = str(result)

        assert "auto" in html

    def test_popover_multiple_content(self) -> None:
        """Test popover with multiple content children."""
        trigger = tags.button("Click", type="button")
        result = popover(
            trigger,
            tags.p("First paragraph"),
            tags.p("Second paragraph"),
        )
        html = str(result)

        assert "First paragraph" in html
        assert "Second paragraph" in html

    def test_popover_with_options(self) -> None:
        """Test popover with custom options."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", options={"animation": True})
        html = str(result)

        # Should include the trigger and content
        assert "Click" in html
        assert "Content" in html

    def test_popover_with_kwargs(self) -> None:
        """Test popover with custom kwargs."""
        trigger = tags.button("Click", type="button")
        result = popover(trigger, "Content", class_="custom-class")
        html = str(result)

        assert "custom-class" in html

    def test_popover_html_content(self) -> None:
        """Test popover with HTML content."""
        trigger = tags.button("Click", type="button")
        content = tags.strong("Bold content")
        result = popover(trigger, content)
        html = str(result)

        assert "<strong>Bold content</strong>" in html

    def test_popover_icon_trigger(self) -> None:
        """Test popover with icon as trigger."""
        trigger = tags.i(class_="fa fa-info-circle")
        result = popover(trigger, "Info content")
        html = str(result)

        assert "fa-info-circle" in html
        assert "Info content" in html

    def test_popover_link_trigger(self) -> None:
        """Test popover with link as trigger."""
        trigger = tags.a("Help", href="#")
        result = popover(trigger, "Help content")
        html = str(result)

        assert "Help" in html
        assert "Help content" in html
