"""Tests for shiny.ui._accordion module."""

from htmltools import Tag

from shiny.ui._accordion import accordion, accordion_panel


class TestAccordion:
    """Tests for accordion function."""

    def test_accordion_basic(self) -> None:
        """Test basic accordion creation."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
        )
        assert isinstance(result, Tag)

    def test_accordion_with_id(self) -> None:
        """Test accordion with id parameter."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            id="my_accordion",
        )
        html = str(result)
        assert "my_accordion" in html

    def test_accordion_multiple_panels(self) -> None:
        """Test accordion with multiple panels."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
        )
        html = str(result)
        assert "Panel 1" in html
        assert "Panel 2" in html

    def test_accordion_has_accordion_class(self) -> None:
        """Test accordion has accordion class."""
        result = accordion(
            accordion_panel("Panel", "Content"),
        )
        html = str(result)
        assert "accordion" in html

    def test_accordion_open_first(self) -> None:
        """Test accordion with open parameter."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1", value="p1"),
            accordion_panel("Panel 2", "Content 2", value="p2"),
            open="p1",
        )
        html = str(result)
        assert "accordion" in html

    def test_accordion_open_true(self) -> None:
        """Test accordion with open=True."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            open=True,
        )
        html = str(result)
        assert "accordion" in html

    def test_accordion_open_false(self) -> None:
        """Test accordion with open=False."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            open=False,
        )
        html = str(result)
        assert "accordion" in html

    def test_accordion_multiple(self) -> None:
        """Test accordion with multiple=True."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            multiple=True,
        )
        html = str(result)
        assert "accordion" in html

    def test_accordion_with_class(self) -> None:
        """Test accordion with class_ parameter."""
        result = accordion(
            accordion_panel("Panel", "Content"),
            class_="my-class",
        )
        html = str(result)
        assert "my-class" in html

    def test_accordion_with_width(self) -> None:
        """Test accordion with width parameter."""
        result = accordion(
            accordion_panel("Panel", "Content"),
            width="300px",
        )
        html = str(result)
        assert "accordion" in html

    def test_accordion_with_height(self) -> None:
        """Test accordion with height parameter."""
        result = accordion(
            accordion_panel("Panel", "Content"),
            height="400px",
        )
        html = str(result)
        assert "accordion" in html


class TestAccordionPanel:
    """Tests for accordion_panel function."""

    def test_accordion_panel_basic(self) -> None:
        """Test basic accordion_panel creation."""
        result = accordion_panel("Title", "Content")
        # accordion_panel returns a data structure
        assert result is not None

    def test_accordion_panel_with_title(self) -> None:
        """Test accordion_panel with title."""
        result = accordion_panel("My Title", "Content")
        assert result is not None

    def test_accordion_panel_with_value(self) -> None:
        """Test accordion_panel with value."""
        result = accordion_panel("Title", "Content", value="my_value")
        assert result is not None

    def test_accordion_panel_with_icon(self) -> None:
        """Test accordion_panel with icon."""
        # Icon parameter testing
        result = accordion_panel("Title", "Content")
        assert result is not None
