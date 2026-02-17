"""Unit tests for shiny.ui._accordion module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import accordion, accordion_panel


class TestAccordionPanel:
    """Tests for accordion_panel function."""

    def test_basic_accordion_panel(self) -> None:
        """Test basic accordion_panel with title and content."""
        panel = accordion_panel("Panel Title", "Panel content")
        assert panel._title == "Panel Title"

    def test_accordion_panel_with_value(self) -> None:
        """Test accordion_panel with custom value."""
        panel = accordion_panel("Title", "Content", value="custom_value")
        assert panel._data_value == "custom_value"

    def test_accordion_panel_with_icon(self) -> None:
        """Test accordion_panel with icon."""
        icon = tags.i(class_="fa fa-info")
        panel = accordion_panel("Title", "Content", icon=icon)
        assert panel._icon is not None

    def test_accordion_panel_multiple_content(self) -> None:
        """Test accordion_panel with multiple content children."""
        panel = accordion_panel(
            "Title",
            tags.p("First paragraph"),
            tags.p("Second paragraph"),
        )
        assert len(panel._args) == 2


class TestAccordion:
    """Tests for accordion function."""

    def test_basic_accordion(self) -> None:
        """Test basic accordion with one panel."""
        panel = accordion_panel("Panel 1", "Content 1")
        result = accordion(panel)

        assert isinstance(result, Tag)
        html = str(result)
        assert "accordion" in html
        assert "Panel 1" in html

    def test_accordion_returns_tag(self) -> None:
        """Test that accordion returns a Tag."""
        panel = accordion_panel("Panel 1", "Content 1")
        result = accordion(panel)
        assert isinstance(result, Tag)

    def test_accordion_with_id(self) -> None:
        """Test accordion with id parameter."""
        panel = accordion_panel("Panel 1", "Content 1")
        result = accordion(panel, id="my_accordion")
        html = str(result)

        assert "my_accordion" in html

    def test_accordion_multiple_panels(self) -> None:
        """Test accordion with multiple panels."""
        panel1 = accordion_panel("Panel 1", "Content 1")
        panel2 = accordion_panel("Panel 2", "Content 2")
        result = accordion(panel1, panel2)

        html = str(result)
        assert "Panel 1" in html
        assert "Panel 2" in html

    def test_accordion_open_first_by_default(self) -> None:
        """Test accordion opens first panel by default."""
        panel1 = accordion_panel("Panel 1", "Content 1", value="p1")
        panel2 = accordion_panel("Panel 2", "Content 2", value="p2")
        result = accordion(panel1, panel2)

        html = str(result)
        # First panel should have "show" class
        assert "show" in html

    def test_accordion_open_specific_panel(self) -> None:
        """Test accordion with specific panel open."""
        panel1 = accordion_panel("Panel 1", "Content 1", value="p1")
        panel2 = accordion_panel("Panel 2", "Content 2", value="p2")
        result = accordion(panel1, panel2, open="p2")

        html = str(result)
        assert "accordion" in html

    def test_accordion_open_all_panels(self) -> None:
        """Test accordion with all panels open."""
        panel1 = accordion_panel("Panel 1", "Content 1")
        panel2 = accordion_panel("Panel 2", "Content 2")
        result = accordion(panel1, panel2, open=True)

        html = str(result)
        assert "accordion" in html

    def test_accordion_close_all_panels(self) -> None:
        """Test accordion with all panels closed."""
        panel1 = accordion_panel("Panel 1", "Content 1")
        panel2 = accordion_panel("Panel 2", "Content 2")
        result = accordion(panel1, panel2, open=False)

        html = str(result)
        assert "accordion" in html

    def test_accordion_multiple_false(self) -> None:
        """Test accordion with multiple=False."""
        panel1 = accordion_panel("Panel 1", "Content 1")
        panel2 = accordion_panel("Panel 2", "Content 2")
        result = accordion(panel1, panel2, multiple=False)

        html = str(result)
        # With multiple=False, should have autoclose class
        assert "autoclose" in html

    def test_accordion_multiple_true(self) -> None:
        """Test accordion with multiple=True (default)."""
        panel1 = accordion_panel("Panel 1", "Content 1")
        panel2 = accordion_panel("Panel 2", "Content 2")
        result = accordion(panel1, panel2, multiple=True)

        html = str(result)
        # Should not have autoclose class
        assert "accordion" in html

    def test_accordion_with_class(self) -> None:
        """Test accordion with custom class."""
        panel = accordion_panel("Panel 1", "Content 1")
        result = accordion(panel, class_="custom-accordion")

        html = str(result)
        assert "custom-accordion" in html

    def test_accordion_with_width(self) -> None:
        """Test accordion with width parameter."""
        panel = accordion_panel("Panel 1", "Content 1")
        result = accordion(panel, width="400px")

        html = str(result)
        assert "400px" in html

    def test_accordion_with_height(self) -> None:
        """Test accordion with height parameter."""
        panel = accordion_panel("Panel 1", "Content 1")
        result = accordion(panel, height="300px")

        html = str(result)
        assert "300px" in html

    def test_accordion_panel_html_content(self) -> None:
        """Test accordion with HTML content in panels."""
        panel = accordion_panel(
            "Title",
            tags.strong("Bold content"),
            tags.em("Italic content"),
        )
        result = accordion(panel)

        html = str(result)
        assert "<strong>Bold content</strong>" in html
        assert "<em>Italic content</em>" in html

    def test_accordion_open_multiple_panels(self) -> None:
        """Test accordion with multiple specific panels open."""
        panel1 = accordion_panel("Panel 1", "Content 1", value="p1")
        panel2 = accordion_panel("Panel 2", "Content 2", value="p2")
        panel3 = accordion_panel("Panel 3", "Content 3", value="p3")
        result = accordion(panel1, panel2, panel3, open=["p1", "p3"])

        html = str(result)
        assert "accordion" in html

    def test_accordion_panel_default_value_from_title(self) -> None:
        """Test that accordion_panel uses title as default value."""
        panel = accordion_panel("My Panel Title", "Content")
        # When value is MISSING, it uses title
        assert panel._title == "My Panel Title"

    def test_accordion_panel_with_kwargs(self) -> None:
        """Test accordion_panel with custom kwargs."""
        panel = accordion_panel(
            "Title",
            "Content",
            class_="custom-panel",
        )
        result = accordion(panel)

        html = str(result)
        assert "custom-panel" in html


class TestAccordionPanelResolve:
    """Tests for AccordionPanel.resolve() method."""

    def test_resolve_returns_tag(self) -> None:
        """Test that resolve returns a Tag."""
        panel = accordion_panel("Title", "Content")
        # Set required properties
        panel._accordion_id = "test_accordion"
        panel._is_multiple = False
        panel._is_open = True

        result = panel.resolve()
        assert isinstance(result, Tag)

    def test_resolve_open_panel(self) -> None:
        """Test resolving an open panel."""
        panel = accordion_panel("Title", "Content")
        panel._accordion_id = "test_accordion"
        panel._is_multiple = False
        panel._is_open = True

        result = panel.resolve()
        html = str(result)
        assert "show" in html
        assert 'aria-expanded="true"' in html

    def test_resolve_closed_panel(self) -> None:
        """Test resolving a closed panel."""
        panel = accordion_panel("Title", "Content")
        panel._accordion_id = "test_accordion"
        panel._is_multiple = False
        panel._is_open = False

        result = panel.resolve()
        html = str(result)
        assert 'aria-expanded="false"' in html
        assert "collapsed" in html
