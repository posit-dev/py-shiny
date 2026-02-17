"""Tests for shiny/ui/_input_select.py module."""

from shiny.ui._input_select import input_select, input_selectize


class TestInputSelect:
    """Tests for input_select function."""

    def test_input_select_is_callable(self):
        """Test input_select is callable."""
        assert callable(input_select)

    def test_input_select_returns_tag(self):
        """Test input_select returns a Tag."""
        from htmltools import Tag

        result = input_select("my_select", "Select option", choices=["A", "B", "C"])
        assert isinstance(result, Tag)

    def test_input_select_with_selected(self):
        """Test input_select with selected parameter."""
        from htmltools import Tag

        result = input_select(
            "my_select", "Select option", choices=["A", "B", "C"], selected="B"
        )
        assert isinstance(result, Tag)

    def test_input_select_with_multiple(self):
        """Test input_select with multiple parameter."""
        from htmltools import Tag

        result = input_select(
            "my_select", "Select options", choices=["A", "B", "C"], multiple=True
        )
        assert isinstance(result, Tag)


class TestInputSelectize:
    """Tests for input_selectize function."""

    def test_input_selectize_is_callable(self):
        """Test input_selectize is callable."""
        assert callable(input_selectize)

    def test_input_selectize_returns_tag(self):
        """Test input_selectize returns a Tag."""
        from htmltools import Tag

        result = input_selectize(
            "my_selectize", "Select option", choices=["A", "B", "C"]
        )
        assert isinstance(result, Tag)

    def test_input_selectize_with_options(self):
        """Test input_selectize with options parameter."""
        from htmltools import Tag

        result = input_selectize(
            "my_selectize",
            "Select option",
            choices=["A", "B", "C"],
            options={"placeholder": "Choose..."},
        )
        assert isinstance(result, Tag)


class TestInputSelectExported:
    """Tests for select functions export."""

    def test_input_select_in_ui(self):
        """Test input_select is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_select")

    def test_input_selectize_in_ui(self):
        """Test input_selectize is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_selectize")
