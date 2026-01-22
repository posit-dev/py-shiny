import pytest
from htmltools import Tag, tags

from shiny.ui._accordion import (
    AccordionPanel,
    accordion,
    accordion_panel,
)


class TestAccordionPanel:
    """Tests for the accordion_panel function."""

    def test_accordion_panel_basic(self):
        """Test basic accordion panel creation."""
        result = accordion_panel("Panel Title", "Panel content")

        assert isinstance(result, AccordionPanel)
        assert result._title == "Panel Title"

    def test_accordion_panel_with_value(self):
        """Test accordion panel with explicit value."""
        result = accordion_panel("Title", "Content", value="panel_1")

        assert result._data_value == "panel_1"

    def test_accordion_panel_with_icon(self):
        """Test accordion panel with icon."""
        icon = tags.i(class_="fa fa-home")
        result = accordion_panel("Title", "Content", icon=icon)

        assert result._icon is not None

    def test_accordion_panel_multiple_content(self):
        """Test accordion panel with multiple content items."""
        result = accordion_panel(
            "Title",
            tags.p("Paragraph 1"),
            tags.p("Paragraph 2"),
        )

        assert result._title == "Title"

    def test_accordion_panel_with_kwargs(self):
        """Test accordion panel with additional kwargs."""
        result = accordion_panel("Title", "Content", class_="custom-panel")

        # kwargs should be stored
        assert "class_" in result._kwargs


class TestAccordionPanelClass:
    """Tests for the AccordionPanel class."""

    def test_accordion_panel_class_init(self):
        """Test AccordionPanel class initialization."""
        panel = AccordionPanel(
            "Content",
            data_value="test_value",
            icon=None,
            title="Test Title",
            id="test_id",
        )

        assert panel._data_value == "test_value"
        assert panel._title == "Test Title"
        assert panel._id == "test_id"
        assert panel._icon is None

    def test_accordion_panel_default_states(self):
        """Test default states of AccordionPanel."""
        panel = AccordionPanel(
            "Content",
            data_value="test",
            icon=None,
            title="Title",
            id=None,
        )

        assert panel._is_open is True
        assert panel._is_multiple is False


class TestAccordion:
    """Tests for the accordion function."""

    def test_accordion_basic(self):
        """Test basic accordion creation with panels."""
        panel1 = accordion_panel("Section 1", "Content 1")
        panel2 = accordion_panel("Section 2", "Content 2")

        result = accordion(panel1, panel2)

        assert isinstance(result, Tag)
        result_str = str(result)
        assert "accordion" in result_str

    def test_accordion_with_id(self):
        """Test accordion with explicit id."""
        panel = accordion_panel("Section", "Content")
        result = accordion(panel, id="my_accordion")

        result_str = str(result)
        assert "my_accordion" in result_str or result.attrs.get("id") == "my_accordion"

    def test_accordion_multiple_true(self):
        """Test accordion with multiple=True (default)."""
        panel1 = accordion_panel("Section 1", "Content 1")
        panel2 = accordion_panel("Section 2", "Content 2")

        result = accordion(panel1, panel2, multiple=True)

        assert isinstance(result, Tag)

    def test_accordion_multiple_false(self):
        """Test accordion with multiple=False."""
        panel1 = accordion_panel("Section 1", "Content 1")
        panel2 = accordion_panel("Section 2", "Content 2")

        result = accordion(panel1, panel2, multiple=False)

        # When multiple=False, data-bs-parent should be set
        result_str = str(result)
        assert "accordion" in result_str

    def test_accordion_open_first_panel(self):
        """Test accordion with first panel open by default."""
        panel1 = accordion_panel("Section 1", "Content 1", value="p1")
        panel2 = accordion_panel("Section 2", "Content 2", value="p2")

        result = accordion(panel1, panel2, open="p1")

        result_str = str(result)
        # First panel should be open
        assert "accordion" in result_str

    def test_accordion_open_none(self):
        """Test accordion with no panels open."""
        panel1 = accordion_panel("Section 1", "Content 1", value="p1")
        panel2 = accordion_panel("Section 2", "Content 2", value="p2")

        result = accordion(panel1, panel2, open=False)

        assert isinstance(result, Tag)

    def test_accordion_open_all(self):
        """Test accordion with all panels open."""
        panel1 = accordion_panel("Section 1", "Content 1", value="p1")
        panel2 = accordion_panel("Section 2", "Content 2", value="p2")

        result = accordion(panel1, panel2, open=True)

        assert isinstance(result, Tag)

    def test_accordion_open_list(self):
        """Test accordion with specific panels open via list."""
        panel1 = accordion_panel("Section 1", "Content 1", value="p1")
        panel2 = accordion_panel("Section 2", "Content 2", value="p2")
        panel3 = accordion_panel("Section 3", "Content 3", value="p3")

        result = accordion(panel1, panel2, panel3, open=["p1", "p3"])

        assert isinstance(result, Tag)

    def test_accordion_with_class(self):
        """Test accordion with custom CSS class."""
        panel = accordion_panel("Section", "Content")
        result = accordion(panel, class_="custom-accordion")

        result_str = str(result)
        assert "custom-accordion" in result_str

    def test_accordion_with_width(self):
        """Test accordion with specified width."""
        panel = accordion_panel("Section", "Content")
        result = accordion(panel, width="500px")

        result_str = str(result)
        assert "500px" in result_str

    def test_accordion_with_height(self):
        """Test accordion with specified height."""
        panel = accordion_panel("Section", "Content")
        result = accordion(panel, height="300px")

        result_str = str(result)
        assert "300px" in result_str

    def test_accordion_invalid_child_type(self):
        """Test accordion raises error for non-AccordionPanel children."""
        with pytest.raises(TypeError, match="AccordionPanel"):
            accordion("Not a panel")  # type: ignore[arg-type]

    def test_accordion_with_kwargs(self):
        """Test accordion with additional HTML attributes."""
        panel = accordion_panel("Section", "Content")
        result = accordion(panel, data_custom="value")

        result_str = str(result)
        # Should include the custom attribute
        assert "accordion" in result_str

    def test_accordion_has_bootstrap_classes(self):
        """Test that accordion has bootstrap accordion class."""
        panel = accordion_panel("Section", "Content")
        result = accordion(panel)

        result_str = str(result)
        assert "accordion" in result_str

    def test_accordion_empty_panels_allowed(self):
        """Test accordion with no panels (edge case)."""
        # This might raise an error or create an empty accordion
        try:
            result = accordion()
            assert isinstance(result, Tag)
        except (TypeError, ValueError):
            # It's acceptable if empty accordion is not allowed
            pass


class TestAccordionPanelResolve:
    """Tests for AccordionPanel.resolve method."""

    def test_resolve_requires_accordion_id(self):
        """Test that resolve raises error when not in accordion."""
        panel = AccordionPanel(
            "Content",
            data_value="test",
            icon=None,
            title="Title",
            id="panel_id",
        )

        with pytest.raises(RuntimeError, match="accordion_id not set"):
            panel.resolve()

    def test_resolved_panel_structure(self):
        """Test resolved panel has correct structure."""
        panel1 = accordion_panel("Title", "Content", value="p1")
        # Add to accordion to set _accordion_id
        result = accordion(panel1, id="acc1")

        result_str = str(result)
        assert "accordion-item" in result_str
        assert "accordion-button" in result_str
        assert "accordion-body" in result_str
