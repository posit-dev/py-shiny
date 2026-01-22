"""Tests for shiny.ui._input_select module."""

from htmltools import Tag

from shiny.ui._input_select import input_select, input_selectize


class TestInputSelect:
    """Tests for input_select function."""

    def test_input_select_basic(self) -> None:
        """Test basic input_select creation."""
        result = input_select("my_select", "Choose:", choices=["a", "b", "c"])
        assert isinstance(result, Tag)

    def test_input_select_has_id(self) -> None:
        """Test input_select has correct id."""
        result = input_select("select_id", "Label", choices=["x", "y"])
        html = str(result)
        assert "select_id" in html

    def test_input_select_with_label(self) -> None:
        """Test input_select with label."""
        result = input_select("select", "Select an option:", choices=["a"])
        html = str(result)
        assert "Select an option:" in html

    def test_input_select_with_dict_choices(self) -> None:
        """Test input_select with dict choices."""
        result = input_select(
            "select", "Label", choices={"a": "Option A", "b": "Option B"}
        )
        html = str(result)
        assert "select" in html

    def test_input_select_with_selected(self) -> None:
        """Test input_select with selected value."""
        result = input_select("select", "Label", choices=["a", "b"], selected="b")
        html = str(result)
        assert "select" in html

    def test_input_select_multiple(self) -> None:
        """Test input_select with multiple=True."""
        result = input_select("select", "Label", choices=["a", "b"], multiple=True)
        html = str(result)
        assert "multiple" in html

    def test_input_select_with_width(self) -> None:
        """Test input_select with width parameter."""
        result = input_select("select", "Label", choices=["a"], width="200px")
        html = str(result)
        assert "select" in html


class TestInputSelectize:
    """Tests for input_selectize function."""

    def test_input_selectize_basic(self) -> None:
        """Test basic input_selectize creation."""
        result = input_selectize("my_selectize", "Choose:", choices=["a", "b"])
        assert isinstance(result, Tag)

    def test_input_selectize_has_id(self) -> None:
        """Test input_selectize has correct id."""
        result = input_selectize("selectize_id", "Label", choices=["x"])
        html = str(result)
        assert "selectize_id" in html

    def test_input_selectize_with_label(self) -> None:
        """Test input_selectize with label."""
        result = input_selectize("selectize", "Pick one:", choices=["a"])
        html = str(result)
        assert "Pick one:" in html

    def test_input_selectize_multiple(self) -> None:
        """Test input_selectize with multiple=True."""
        result = input_selectize(
            "selectize", "Label", choices=["a", "b"], multiple=True
        )
        html = str(result)
        assert "selectize" in html

    def test_input_selectize_with_selected(self) -> None:
        """Test input_selectize with selected value."""
        result = input_selectize("selectize", "Label", choices=["a", "b"], selected="a")
        html = str(result)
        assert "selectize" in html

    def test_input_selectize_with_width(self) -> None:
        """Test input_selectize with width parameter."""
        result = input_selectize("selectize", "Label", choices=["a"], width="300px")
        html = str(result)
        assert "selectize" in html

    def test_input_selectize_remove_button(self) -> None:
        """Test input_selectize with remove_button."""
        result = input_selectize(
            "selectize", "Label", choices=["a"], remove_button=True
        )
        html = str(result)
        assert "selectize" in html

    def test_input_selectize_options(self) -> None:
        """Test input_selectize with options dict."""
        result = input_selectize(
            "selectize", "Label", choices=["a"], options={"maxItems": 5}
        )
        html = str(result)
        assert "selectize" in html
