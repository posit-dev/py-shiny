"""Tests for accordion UI components."""

from shiny.ui import (
    accordion,
    accordion_panel,
)


class TestAccordionPanel:
    """Tests for accordion_panel function."""

    def test_basic_accordion_panel(self):
        """Test creating a basic accordion panel."""
        panel = accordion_panel("Panel Title", "Panel content")
        assert panel is not None
        assert panel._data_value == "Panel Title"

    def test_accordion_panel_with_value(self):
        """Test accordion panel with explicit value."""
        panel = accordion_panel("Display Title", "Content", value="panel_id")
        assert panel._data_value == "panel_id"

    def test_accordion_panel_with_icon(self):
        """Test accordion panel with icon."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-cog")
        panel = accordion_panel("Settings", "Settings content", icon=icon)
        assert panel is not None
        assert panel._icon is not None


class TestAccordion:
    """Tests for accordion function."""

    def test_basic_accordion(self):
        """Test creating a basic accordion."""
        acc = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
        )
        html = str(acc)

        assert "accordion" in html
        assert "Panel 1" in html
        assert "Panel 2" in html

    def test_accordion_with_id(self):
        """Test accordion with id."""
        acc = accordion(accordion_panel("Panel 1", "Content 1"), id="my_accordion")
        html = str(acc)

        assert "my_accordion" in html

    def test_accordion_open_panels(self):
        """Test accordion with specific panels open."""
        acc = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            open="Panel 1",
        )
        html = str(acc)

        assert "Panel 1" in html

    def test_accordion_open_all(self):
        """Test accordion with all panels open."""
        acc = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            open=True,
        )
        html = str(acc)

        assert "Panel 1" in html

    def test_accordion_multiple(self):
        """Test accordion that allows multiple panels open."""
        acc = accordion(
            accordion_panel("Panel 1", "Content 1"),
            accordion_panel("Panel 2", "Content 2"),
            multiple=True,
        )
        html = str(acc)

        assert "accordion" in html

    def test_accordion_width(self):
        """Test accordion with explicit width."""
        acc = accordion(accordion_panel("Panel 1", "Content 1"), width="400px")
        html = str(acc)

        assert "400px" in html

    def test_accordion_height(self):
        """Test accordion with explicit height."""
        acc = accordion(accordion_panel("Panel 1", "Content 1"), height="300px")
        html = str(acc)

        assert "300px" in html
