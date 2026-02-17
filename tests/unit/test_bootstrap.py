"""Tests for shiny/ui/_bootstrap.py"""

import pytest
from htmltools import Tag, TagList

from shiny.ui import (
    column,
    help_text,
    panel_absolute,
    panel_conditional,
    panel_fixed,
    panel_title,
    row,
)


class TestRow:
    """Tests for the row function."""

    def test_basic_row(self):
        """Test basic row creation."""
        result = row("Content")
        html = str(result)
        assert "<div" in html
        assert 'class="row"' in html
        assert "Content" in html

    def test_row_returns_tag(self):
        """Test row returns a Tag."""
        result = row()
        assert isinstance(result, Tag)

    def test_row_with_multiple_children(self):
        """Test row with multiple child elements."""
        result = row("Child 1", "Child 2", "Child 3")
        html = str(result)
        assert "Child 1" in html
        assert "Child 2" in html
        assert "Child 3" in html

    def test_row_with_kwargs(self):
        """Test row with additional attributes."""
        result = row("Content", id="my-row", data_custom="value")
        html = str(result)
        assert 'id="my-row"' in html
        assert 'data-custom="value"' in html


class TestColumn:
    """Tests for the column function."""

    def test_basic_column(self):
        """Test basic column creation."""
        result = column(6, "Content")
        html = str(result)
        assert "<div" in html
        assert "col-sm-6" in html
        assert "Content" in html

    def test_column_returns_tag(self):
        """Test column returns a Tag."""
        result = column(4)
        assert isinstance(result, Tag)

    def test_column_width_1(self):
        """Test column with width 1."""
        result = column(1, "Narrow")
        html = str(result)
        assert "col-sm-1" in html

    def test_column_width_12(self):
        """Test column with width 12."""
        result = column(12, "Full width")
        html = str(result)
        assert "col-sm-12" in html

    def test_column_invalid_width_0(self):
        """Test column raises error for width 0."""
        with pytest.raises(ValueError, match="Column width must be between 1 and 12"):
            column(0, "Content")

    def test_column_invalid_width_13(self):
        """Test column raises error for width 13."""
        with pytest.raises(ValueError, match="Column width must be between 1 and 12"):
            column(13, "Content")

    def test_column_with_offset(self):
        """Test column with offset."""
        result = column(6, "Content", offset=3)
        html = str(result)
        assert "col-sm-6" in html
        assert "offset-md-3" in html
        assert "col-sm-offset-3" in html

    def test_column_zero_offset(self):
        """Test column with zero offset (no offset classes)."""
        result = column(6, "Content", offset=0)
        html = str(result)
        assert "col-sm-6" in html
        assert "offset-md" not in html
        assert "col-sm-offset" not in html

    def test_column_with_kwargs(self):
        """Test column with additional attributes."""
        result = column(4, "Content", id="my-col", data_custom="value")
        html = str(result)
        assert 'id="my-col"' in html
        assert 'data-custom="value"' in html


class TestPanelConditional:
    """Tests for the panel_conditional function."""

    def test_basic_panel_conditional(self):
        """Test basic conditional panel creation."""
        result = panel_conditional("input.checkbox", "Conditional content")
        html = str(result)
        assert "<div" in html
        assert "shiny-panel-conditional" in html
        assert 'data-display-if="input.checkbox"' in html
        assert "Conditional content" in html

    def test_panel_conditional_returns_tag(self):
        """Test panel_conditional returns a Tag."""
        result = panel_conditional("true")
        assert isinstance(result, Tag)

    def test_panel_conditional_js_expression(self):
        """Test panel_conditional with complex JS expression."""
        result = panel_conditional("input.foo > 5 && output.bar")
        html = str(result)
        assert 'data-display-if="input.foo &gt; 5 &amp;&amp; output.bar"' in html

    def test_panel_conditional_with_multiple_children(self):
        """Test panel_conditional with multiple children."""
        result = panel_conditional("input.show", "Child 1", "Child 2")
        html = str(result)
        assert "Child 1" in html
        assert "Child 2" in html

    def test_panel_conditional_has_ns_prefix(self):
        """Test panel_conditional has data-ns-prefix attribute."""
        result = panel_conditional("input.test")
        html = str(result)
        assert "data-ns-prefix" in html

    def test_panel_conditional_with_kwargs(self):
        """Test panel_conditional with additional attributes."""
        result = panel_conditional("true", "Content", id="my-panel", class_="custom")
        html = str(result)
        assert 'id="my-panel"' in html
        assert "custom" in html


class TestPanelTitle:
    """Tests for the panel_title function."""

    def test_basic_panel_title(self):
        """Test basic panel title creation."""
        result = panel_title("My App Title")
        assert isinstance(result, TagList)
        html = str(result)
        assert "<h2" in html
        assert "My App Title" in html

    def test_panel_title_returns_taglist(self):
        """Test panel_title returns a TagList."""
        result = panel_title("Title")
        assert isinstance(result, TagList)

    def test_panel_title_with_tag(self):
        """Test panel_title with a Tag as title."""
        from htmltools import h1

        result = panel_title(h1("Custom Header"))
        html = str(result)
        assert "<h1" in html
        assert "Custom Header" in html

    def test_panel_title_with_window_title(self):
        """Test panel_title with custom window title."""
        result = panel_title("Display Title", window_title="Browser Tab Title")
        html = str(result)
        assert "Display Title" in html
        # The title tag is in the head dependencies
        assert "<h2" in html


class TestPanelFixed:
    """Tests for the panel_fixed function."""

    def test_basic_panel_fixed(self):
        """Test basic fixed panel creation."""
        result = panel_fixed("Fixed content")
        html = str(result)
        assert "Fixed content" in html
        assert "position:fixed" in html

    def test_panel_fixed_returns_taglist(self):
        """Test panel_fixed returns a TagList."""
        result = panel_fixed("Content")
        assert isinstance(result, TagList)

    def test_panel_fixed_with_position(self):
        """Test panel_fixed with position attributes."""
        result = panel_fixed("Content", top="10px", left="20px")
        html = str(result)
        assert "top:10px" in html
        assert "left:20px" in html

    def test_panel_fixed_with_size(self):
        """Test panel_fixed with width and height."""
        result = panel_fixed("Content", width="300px", height="200px")
        html = str(result)
        assert "width:300px" in html
        assert "height:200px" in html

    def test_panel_fixed_draggable(self):
        """Test panel_fixed with draggable option."""
        result = panel_fixed("Drag me", draggable=True)
        html = str(result)
        assert "draggable" in html
        assert "cursor:move" in html


class TestPanelAbsolute:
    """Tests for the panel_absolute function."""

    def test_basic_panel_absolute(self):
        """Test basic absolute panel creation."""
        result = panel_absolute("Absolute content")
        html = str(result)
        assert "Absolute content" in html
        assert "position:absolute" in html

    def test_panel_absolute_returns_taglist(self):
        """Test panel_absolute returns a TagList."""
        result = panel_absolute("Content")
        assert isinstance(result, TagList)

    def test_panel_absolute_with_top_left(self):
        """Test panel_absolute with top and left."""
        result = panel_absolute("Content", top="50px", left="100px")
        html = str(result)
        assert "top:50px" in html
        assert "left:100px" in html

    def test_panel_absolute_with_bottom_right(self):
        """Test panel_absolute with bottom and right."""
        result = panel_absolute("Content", bottom="0", right="0")
        html = str(result)
        assert "bottom:0" in html
        assert "right:0" in html

    def test_panel_absolute_with_size(self):
        """Test panel_absolute with width and height."""
        result = panel_absolute("Content", width="50%", height="200px")
        html = str(result)
        assert "width:50%" in html
        assert "height:200px" in html

    def test_panel_absolute_not_fixed(self):
        """Test panel_absolute is not fixed by default."""
        result = panel_absolute("Content")
        html = str(result)
        assert "position:absolute" in html
        assert "position:fixed" not in html

    def test_panel_absolute_fixed_true(self):
        """Test panel_absolute with fixed=True."""
        result = panel_absolute("Content", fixed=True)
        html = str(result)
        assert "position:fixed" in html

    def test_panel_absolute_draggable(self):
        """Test panel_absolute with draggable."""
        result = panel_absolute("Drag me", draggable=True)
        html = str(result)
        assert "draggable" in html
        assert "cursor:move" in html

    def test_panel_absolute_cursor_default(self):
        """Test panel_absolute with cursor default."""
        result = panel_absolute("Content", cursor="default")
        html = str(result)
        assert "cursor:default" in html

    def test_panel_absolute_cursor_inherit(self):
        """Test panel_absolute with cursor inherit."""
        result = panel_absolute("Content", cursor="inherit")
        html = str(result)
        assert "cursor:inherit" in html

    def test_panel_absolute_cursor_move(self):
        """Test panel_absolute with cursor move."""
        result = panel_absolute("Content", cursor="move")
        html = str(result)
        assert "cursor:move" in html

    def test_panel_absolute_with_kwargs(self):
        """Test panel_absolute with additional attributes."""
        result = panel_absolute("Content", id="my-panel", data_custom="value")
        html = str(result)
        assert 'id="my-panel"' in html
        assert 'data-custom="value"' in html


class TestHelpText:
    """Tests for the help_text function."""

    def test_basic_help_text(self):
        """Test basic help text creation."""
        result = help_text("This is help text")
        html = str(result)
        assert "<span" in html
        assert "help-block" in html
        assert "This is help text" in html

    def test_help_text_returns_tag(self):
        """Test help_text returns a Tag."""
        result = help_text("Text")
        assert isinstance(result, Tag)

    def test_help_text_with_multiple_children(self):
        """Test help_text with multiple children."""
        result = help_text("Part 1", " - ", "Part 2")
        html = str(result)
        assert "Part 1" in html
        assert " - " in html
        assert "Part 2" in html

    def test_help_text_with_kwargs(self):
        """Test help_text with additional attributes."""
        result = help_text("Help", id="my-help", data_custom="value")
        html = str(result)
        assert 'id="my-help"' in html
        assert 'data-custom="value"' in html
