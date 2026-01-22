"""Tests for `shiny.ui._tooltip` and `shiny.ui._popover`."""

from htmltools import tags

from shiny.ui import popover, tooltip


class TestTooltip:
    """Tests for the tooltip function."""

    def test_basic_tooltip(self):
        """Test creating a basic tooltip."""
        t = tooltip(
            tags.button("Hover me"),
            "This is tooltip content",
        )
        html = str(t)

        assert "bslib-tooltip" in html
        assert "Hover me" in html
        assert "This is tooltip content" in html

    def test_tooltip_with_id(self):
        """Test tooltip with an id for reactive updates."""
        t = tooltip(
            tags.button("Hover me"),
            "Tooltip content",
            id="my_tooltip",
        )
        html = str(t)

        assert "my_tooltip" in html

    def test_tooltip_placement(self):
        """Test tooltip with different placements."""
        for placement in ["top", "bottom", "left", "right", "auto"]:
            t = tooltip(
                tags.button("Button"),
                "Content",
                placement=placement,  # type: ignore
            )
            html = str(t)
            assert f'placement="{placement}"' in html or placement in html

    def test_tooltip_with_options(self):
        """Test tooltip with custom Bootstrap options."""
        t = tooltip(
            tags.button("Button"),
            "Content",
            options={"animation": False, "delay": 100},
        )
        html = str(t)

        # Options should be serialized
        assert "bslib-tooltip" in html

    def test_tooltip_with_multiple_content(self):
        """Test tooltip with multiple content elements."""
        t = tooltip(
            tags.button("Trigger"),
            "Line 1",
            tags.br(),
            "Line 2",
        )
        html = str(t)

        assert "Line 1" in html
        assert "Line 2" in html

    def test_tooltip_with_custom_attributes(self):
        """Test tooltip with custom attributes."""
        t = tooltip(
            tags.button("Trigger"),
            "Content",
            class_="my-tooltip-class",
        )
        html = str(t)

        assert "my-tooltip-class" in html


class TestPopover:
    """Tests for the popover function."""

    def test_basic_popover(self):
        """Test creating a basic popover."""
        p = popover(
            tags.button("Click me"),
            "This is popover content",
        )
        html = str(p)

        assert "bslib-popover" in html
        assert "Click me" in html
        assert "This is popover content" in html

    def test_popover_with_title(self):
        """Test popover with a title."""
        p = popover(
            tags.button("Click"),
            "Body content",
            title="Popover Title",
        )
        html = str(p)

        assert "Popover Title" in html
        assert "Body content" in html

    def test_popover_with_id(self):
        """Test popover with an id for reactive updates."""
        p = popover(
            tags.button("Click"),
            "Content",
            id="my_popover",
        )
        html = str(p)

        assert "my_popover" in html

    def test_popover_placement(self):
        """Test popover with different placements."""
        for placement in ["top", "bottom", "left", "right", "auto"]:
            p = popover(
                tags.button("Button"),
                "Content",
                placement=placement,  # type: ignore
            )
            html = str(p)
            assert f'placement="{placement}"' in html or placement in html

    def test_popover_with_options(self):
        """Test popover with custom Bootstrap options."""
        p = popover(
            tags.button("Button"),
            "Content",
            options={"animation": False, "trigger": "focus"},
        )
        html = str(p)

        assert "bslib-popover" in html

    def test_popover_with_complex_content(self):
        """Test popover with complex nested content."""
        p = popover(
            tags.button("Settings"),
            tags.div(
                tags.p("Configure options:"),
                tags.input(type="text", placeholder="Enter value"),
            ),
            title="Settings",
        )
        html = str(p)

        assert "Configure options:" in html
        assert "Settings" in html
        assert '<input type="text"' in html

    def test_popover_with_custom_attributes(self):
        """Test popover with custom attributes."""
        p = popover(
            tags.button("Trigger"),
            "Content",
            class_="my-popover-class",
            data_custom="value",
        )
        html = str(p)

        assert "my-popover-class" in html
