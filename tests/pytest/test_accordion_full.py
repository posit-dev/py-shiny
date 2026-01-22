"""Tests for shiny/ui/_accordion.py module."""

from shiny.ui._accordion import AccordionPanel, accordion, accordion_panel


class TestAccordion:
    """Tests for accordion function."""

    def test_accordion_is_callable(self):
        """Test accordion is callable."""
        assert callable(accordion)

    def test_accordion_returns_tag(self):
        """Test accordion returns a Tag."""
        from htmltools import Tag

        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
        )
        assert isinstance(result, Tag)

    def test_accordion_with_id(self):
        """Test accordion with id parameter."""
        from htmltools import Tag

        result = accordion(
            accordion_panel("Panel 1", "Content 1"),
            id="my_accordion",
        )
        assert isinstance(result, Tag)


class TestAccordionPanel:
    """Tests for accordion_panel function."""

    def test_accordion_panel_is_callable(self):
        """Test accordion_panel is callable."""
        assert callable(accordion_panel)

    def test_accordion_panel_returns_accordion_panel(self):
        """Test accordion_panel returns an AccordionPanel object."""
        result = accordion_panel("Panel Title", "Content")
        assert isinstance(result, AccordionPanel)


class TestAccordionPanelClass:
    """Tests for AccordionPanel class."""

    def test_accordion_panel_class_exists(self):
        """Test AccordionPanel class exists."""
        assert AccordionPanel is not None


class TestAccordionExported:
    """Tests for accordion functions export."""

    def test_accordion_in_ui(self):
        """Test accordion is in ui module."""
        from shiny import ui

        assert hasattr(ui, "accordion")

    def test_accordion_panel_in_ui(self):
        """Test accordion_panel is in ui module."""
        from shiny import ui

        assert hasattr(ui, "accordion_panel")

    def test_update_accordion_in_ui(self):
        """Test update_accordion is in ui module."""
        from shiny import ui

        assert hasattr(ui, "update_accordion")

    def test_update_accordion_panel_in_ui(self):
        """Test update_accordion_panel is in ui module."""
        from shiny import ui

        assert hasattr(ui, "update_accordion_panel")
