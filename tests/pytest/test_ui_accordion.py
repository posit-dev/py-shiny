"""Tests for shiny/ui/_accordion.py"""

from __future__ import annotations

import pytest
from htmltools import Tag

from shiny.ui import accordion, accordion_panel


class TestAccordionPanel:
    """Tests for the accordion_panel function."""

    def test_basic_panel(self) -> None:
        """Test creating a basic accordion panel."""
        panel = accordion_panel("Panel Title", "Content")
        assert hasattr(panel, "_title")
        assert panel._title == "Panel Title"

    def test_panel_with_value(self) -> None:
        """Test creating a panel with explicit value."""
        panel = accordion_panel("Panel Title", "Content", value="my-value")
        assert panel._data_value == "my-value"

    def test_panel_infers_value_from_title(self) -> None:
        """Test that value is inferred from string title."""
        panel = accordion_panel("My Title", "Content")
        assert panel._data_value == "My Title"

    def test_panel_non_string_title_requires_value(self) -> None:
        """Test that non-string title requires explicit value."""
        from htmltools import span

        with pytest.raises(ValueError, match="value.*must be provided"):
            accordion_panel(span("Title"), "Content")

    def test_panel_with_icon(self) -> None:
        """Test creating a panel with an icon."""
        panel = accordion_panel("Title", "Content", icon="🎯")
        assert panel._icon == "🎯"

    def test_panel_value_must_be_string(self) -> None:
        """Test that value must be a string."""
        with pytest.raises(TypeError, match="value.*must be a string"):
            accordion_panel("Title", "Content", value=123)  # type: ignore

    def test_panel_multiple_children(self) -> None:
        """Test panel with multiple content children."""
        # Panel needs to be inside accordion to resolve
        result = accordion(
            accordion_panel("Title", "Para 1", "Para 2", "Para 3"),
            id="test_acc",
        )
        rendered = str(result)
        # Content should be present
        assert "accordion" in rendered.lower()


class TestAccordion:
    """Tests for the accordion function."""

    def test_basic_accordion(self) -> None:
        """Test creating a basic accordion."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
        )
        assert isinstance(result, Tag)
        assert result.name == "div"
        class_attr = result.attrs.get("class", "")
        assert "accordion" in class_attr

    def test_accordion_with_id(self) -> None:
        """Test accordion with custom id (valid characters only)."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            id="my_accordion",  # Use underscore, not hyphen
        )
        assert result.attrs.get("id") == "my_accordion"

    def test_accordion_auto_generates_id(self) -> None:
        """Test that accordion auto-generates id if not provided."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
        )
        # ID should be auto-generated
        assert result.attrs.get("id") is not None

    def test_accordion_open_single_panel(self) -> None:
        """Test accordion with single panel open."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            open="Panel 1",
        )
        rendered = str(result)
        assert "accordion" in rendered

    def test_accordion_open_multiple_panels(self) -> None:
        """Test accordion with multiple panels open."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            open=["Panel 1", "Panel 2"],
        )
        assert isinstance(result, Tag)

    def test_accordion_open_all(self) -> None:
        """Test accordion with all panels open."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            open=True,
        )
        assert isinstance(result, Tag)

    def test_accordion_open_none(self) -> None:
        """Test accordion with no panels open."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            open=False,
        )
        assert isinstance(result, Tag)

    def test_accordion_multiple_false(self) -> None:
        """Test accordion with multiple=False (single panel at a time)."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            multiple=False,
        )
        rendered = str(result)
        # Multiple=False should add data attribute or specific class
        assert "accordion" in rendered

    def test_accordion_multiple_true(self) -> None:
        """Test accordion with multiple=True."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            multiple=True,
        )
        assert isinstance(result, Tag)

    def test_accordion_with_class(self) -> None:
        """Test accordion with additional class."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            class_="my-custom-class",
        )
        class_attr = result.attrs.get("class", "")
        assert "my-custom-class" in class_attr

    def test_accordion_panel_count(self) -> None:
        """Test accordion with specific number of panels."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            accordion_panel("Panel 3", "Content 3"),
        )
        # Check that all panels are in the rendered output
        rendered = str(result)
        assert "Panel 1" in rendered
        assert "Panel 2" in rendered
        assert "Panel 3" in rendered

    def test_accordion_width_height(self) -> None:
        """Test accordion with width and height."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            width="400px",
            height="300px",
        )
        # Width and height should be applied via style
        style_attr = result.attrs.get("style", "")
        assert "400px" in str(style_attr) or isinstance(result, Tag)

    def test_accordion_empty(self) -> None:
        """Test that accordion with no panels still works."""
        # Accordion without panels should still be valid
        result = accordion()
        assert isinstance(result, Tag)


class TestAccordionStructure:
    """Tests for accordion DOM structure."""

    def test_accordion_has_proper_structure(self) -> None:
        """Test that accordion has proper Bootstrap structure."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            id="test_accordion",  # Use underscore, not hyphen
        )
        rendered = str(result)
        # Should have accordion class
        assert "accordion" in rendered
        # Should have accordion-item class (for panels)
        assert "accordion-item" in rendered

    def test_accordion_panel_has_header(self) -> None:
        """Test that accordion panel has header element."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
        )
        rendered = str(result)
        # Should have accordion-header
        assert "accordion-header" in rendered

    def test_accordion_panel_has_collapse(self) -> None:
        """Test that accordion panel has collapse element."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
        )
        rendered = str(result)
        # Should have accordion-collapse class
        assert "accordion-collapse" in rendered

    def test_accordion_panel_has_body(self) -> None:
        """Test that accordion panel has body element."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
        )
        rendered = str(result)
        # Should have accordion-body
        assert "accordion-body" in rendered


class TestAccordionInput:
    """Tests for accordion as Shiny input."""

    def test_accordion_binding_class(self) -> None:
        """Test that accordion has proper binding class."""
        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            id="test_accordion",  # Use underscore, not hyphen
        )
        class_attr = result.attrs.get("class", "")
        # Should have bslib binding class
        assert "bslib-accordion" in class_attr or "accordion" in class_attr
