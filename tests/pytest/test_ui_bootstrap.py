"""Tests for shiny/ui/_bootstrap.py - Bootstrap layout components."""

import pytest
from htmltools import TagList

from shiny.ui._bootstrap import (
    column,
    help_text,
    panel_absolute,
    panel_conditional,
    panel_fixed,
    panel_title,
    panel_well,
    row,
)


class TestRow:
    """Tests for row function."""

    def test_row_basic(self):
        """Test basic row creation."""
        r = row("content")
        html = str(r)
        assert '<div class="row">' in html
        assert "content" in html

    def test_row_with_children(self):
        """Test row with multiple children."""
        r = row("child1", "child2", "child3")
        html = str(r)
        assert "child1" in html
        assert "child2" in html
        assert "child3" in html

    def test_row_with_kwargs(self):
        """Test row with additional attributes."""
        r = row("content", id="my-row", style="background: red;")
        html = str(r)
        assert 'id="my-row"' in html
        assert "background: red" in html


class TestColumn:
    """Tests for column function."""

    def test_column_basic(self):
        """Test basic column creation."""
        c = column(6, "content")
        html = str(c)
        assert "col-sm-6" in html
        assert "content" in html

    def test_column_with_offset(self):
        """Test column with offset."""
        c = column(6, "content", offset=3)
        html = str(c)
        assert "col-sm-6" in html
        assert "offset-md-3" in html
        assert "col-sm-offset-3" in html

    def test_column_width_validation_too_low(self):
        """Test column width validation - too low."""
        with pytest.raises(ValueError, match="between 1 and 12"):
            column(0, "content")

    def test_column_width_validation_too_high(self):
        """Test column width validation - too high."""
        with pytest.raises(ValueError, match="between 1 and 12"):
            column(13, "content")

    def test_column_width_boundary_low(self):
        """Test column width at lower boundary."""
        c = column(1, "content")
        html = str(c)
        assert "col-sm-1" in html

    def test_column_width_boundary_high(self):
        """Test column width at upper boundary."""
        c = column(12, "content")
        html = str(c)
        assert "col-sm-12" in html


class TestPanelWell:
    """Tests for panel_well function (deprecated)."""

    def test_panel_well_returns_div(self):
        """Test panel_well returns div with well class."""
        import warnings

        from shiny._deprecated import ShinyDeprecationWarning

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = panel_well("content")
            assert len(w) >= 1
            # Check that at least one warning is about deprecation
            assert any(
                issubclass(warning.category, ShinyDeprecationWarning) for warning in w
            )
        html = str(result)
        assert "well" in html
        assert "content" in html


class TestPanelConditional:
    """Tests for panel_conditional function."""

    def test_panel_conditional_basic(self):
        """Test basic conditional panel."""
        panel = panel_conditional("input.show === true", "content")
        html = str(panel)
        assert "shiny-panel-conditional" in html
        assert 'data-display-if="input.show === true"' in html
        assert "content" in html

    def test_panel_conditional_with_kwargs(self):
        """Test conditional panel with additional attributes."""
        panel = panel_conditional("input.visible", "content", id="my-panel")
        html = str(panel)
        assert 'id="my-panel"' in html

    def test_panel_conditional_has_ns_prefix(self):
        """Test conditional panel has namespace prefix data attribute."""
        panel = panel_conditional("input.test", "content")
        html = str(panel)
        assert "data-ns-prefix" in html


class TestPanelTitle:
    """Tests for panel_title function."""

    def test_panel_title_string(self):
        """Test panel_title with string."""
        result = panel_title("My Title")
        assert isinstance(result, TagList)
        html = str(result)
        assert "My Title" in html
        assert "<h2>" in html

    def test_panel_title_with_window_title(self):
        """Test panel_title with explicit window title."""
        result = panel_title("UI Title", window_title="Browser Title")
        html = str(result)
        assert "UI Title" in html


class TestPanelAbsolute:
    """Tests for panel_absolute function."""

    def test_panel_absolute_basic(self):
        """Test basic absolute panel."""
        result = panel_absolute("content")
        html = str(result)
        assert "content" in html
        assert "position:absolute" in html

    def test_panel_absolute_with_position(self):
        """Test absolute panel with position."""
        result = panel_absolute("content", top="10px", left="20px")
        html = str(result)
        assert "top:10px" in html
        assert "left:20px" in html

    def test_panel_absolute_with_size(self):
        """Test absolute panel with size."""
        result = panel_absolute("content", width="100px", height="200px")
        html = str(result)
        assert "width:100px" in html
        assert "height:200px" in html

    def test_panel_absolute_fixed(self):
        """Test absolute panel with fixed position."""
        result = panel_absolute("content", fixed=True)
        html = str(result)
        assert "position:fixed" in html

    def test_panel_absolute_draggable(self):
        """Test draggable absolute panel."""
        result = panel_absolute("content", draggable=True)
        html = str(result)
        assert "draggable" in html
        assert "cursor:move" in html

    def test_panel_absolute_cursor_options(self):
        """Test cursor options for absolute panel."""
        result = panel_absolute("content", cursor="move")
        html = str(result)
        assert "cursor:move" in html

        result = panel_absolute("content", cursor="default")
        html = str(result)
        assert "cursor:default" in html


class TestPanelFixed:
    """Tests for panel_fixed function."""

    def test_panel_fixed_basic(self):
        """Test basic fixed panel."""
        result = panel_fixed("content")
        html = str(result)
        assert "content" in html
        assert "position:fixed" in html

    def test_panel_fixed_with_position(self):
        """Test fixed panel with position."""
        result = panel_fixed("content", top="0", right="0")
        html = str(result)
        assert "top:0" in html
        assert "right:0" in html


class TestHelpText:
    """Tests for help_text function."""

    def test_help_text_basic(self):
        """Test basic help text."""
        result = help_text("This is help text")
        html = str(result)
        assert "help-block" in html
        assert "This is help text" in html

    def test_help_text_with_kwargs(self):
        """Test help text with additional attributes."""
        result = help_text("Help", id="my-help")
        html = str(result)
        assert 'id="my-help"' in html

    def test_help_text_multiple_children(self):
        """Test help text with multiple children."""
        result = help_text("Line 1", " ", "Line 2")
        html = str(result)
        assert "Line 1" in html
        assert "Line 2" in html
