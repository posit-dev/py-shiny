"""Unit tests for shiny.ui._input_select module."""

from __future__ import annotations

import warnings

from htmltools import Tag

from shiny.ui import input_select, input_selectize


class TestInputSelect:
    """Tests for input_select function."""

    def test_basic_input_select_list(self) -> None:
        """Test basic input_select with list choices."""
        result = input_select("sel_id", "Select", ["a", "b", "c"])
        html = str(result)

        assert 'id="sel_id"' in html
        assert "Select" in html
        assert "<select" in html
        assert "<option" in html
        assert 'value="a"' in html
        assert 'value="b"' in html
        assert 'value="c"' in html

    def test_input_select_returns_tag(self) -> None:
        """Test that input_select returns a Tag."""
        result = input_select("sel_id", "Select", ["a"])
        assert isinstance(result, Tag)

    def test_input_select_tuple_choices(self) -> None:
        """Test input_select with tuple choices."""
        result = input_select("sel_id", "Select", ("x", "y", "z"))
        html = str(result)

        assert 'value="x"' in html
        assert 'value="y"' in html
        assert 'value="z"' in html

    def test_input_select_dict_choices(self) -> None:
        """Test input_select with dict choices."""
        result = input_select("sel_id", "Select", {"a": "Choice A", "b": "Choice B"})
        html = str(result)

        assert 'value="a"' in html
        assert 'value="b"' in html
        assert "Choice A" in html
        assert "Choice B" in html

    def test_input_select_selected(self) -> None:
        """Test input_select with selected value."""
        result = input_select("sel_id", "Select", ["a", "b", "c"], selected="b")
        html = str(result)

        # The selected option should have selected attribute
        assert 'value="b"' in html

    def test_input_select_selected_list(self) -> None:
        """Test input_select with list of selected values."""
        result = input_select(
            "sel_id", "Select", ["a", "b", "c"], selected=["a", "c"], multiple=True
        )
        html = str(result)

        assert 'value="a"' in html
        assert 'value="c"' in html

    def test_input_select_multiple_true(self) -> None:
        """Test input_select with multiple=True."""
        result = input_select("sel_id", "Select", ["a", "b"], multiple=True)
        html = str(result)

        assert "multiple" in html

    def test_input_select_multiple_false(self) -> None:
        """Test input_select with multiple=False."""
        result = input_select("sel_id", "Select", ["a", "b"], multiple=False)
        html = str(result)

        # multiple should not be present
        assert 'multiple="' not in html or "multiple" not in html

    def test_input_select_with_width(self) -> None:
        """Test input_select with width parameter."""
        result = input_select("sel_id", "Select", ["a"], width="300px")
        html = str(result)

        assert "width:300px" in html

    def test_input_select_with_size(self) -> None:
        """Test input_select with size parameter."""
        result = input_select("sel_id", "Select", ["a", "b", "c"], size="5")
        html = str(result)

        assert 'size="5"' in html

    def test_input_select_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_select("sel_id", "Select", ["a"])
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_select_form_select_class(self) -> None:
        """Test that select has form-select class (non-selectize)."""
        result = input_select("sel_id", "Select", ["a"])
        html = str(result)

        assert "form-select" in html

    def test_input_select_shiny_input_select_class(self) -> None:
        """Test that select has shiny-input-select class."""
        result = input_select("sel_id", "Select", ["a"])
        html = str(result)

        assert "shiny-input-select" in html

    def test_input_select_html_label(self) -> None:
        """Test input_select with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Select")
        result = input_select("sel_id", label, ["a", "b"])
        html = str(result)

        assert "<strong>Bold Select</strong>" in html

    def test_input_select_optgroup_choices(self) -> None:
        """Test input_select with optgroup choices."""
        result = input_select(
            "sel_id",
            "Select",
            {"Group A": {"a1": "A1", "a2": "A2"}, "Group B": {"b1": "B1"}},
        )
        html = str(result)

        assert "<optgroup" in html
        assert 'label="Group A"' in html
        assert 'label="Group B"' in html
        assert 'value="a1"' in html
        assert 'value="b1"' in html

    def test_input_select_default_selects_first(self) -> None:
        """Test input_select default selects first option when not multiple."""
        result = input_select("sel_id", "Select", ["first", "second"])
        html = str(result)

        # First option should be selected by default
        assert 'value="first"' in html

    def test_input_select_deprecated_selectize_warning(self) -> None:
        """Test input_select selectize parameter raises deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            input_select("sel_id", "Select", ["a"], selectize=True)
            assert len(w) >= 1
            assert "deprecated" in str(w[0].message).lower()


class TestInputSelectize:
    """Tests for input_selectize function."""

    def test_basic_input_selectize(self) -> None:
        """Test basic input_selectize with list choices."""
        result = input_selectize("selz_id", "Selectize", ["a", "b", "c"])
        html = str(result)

        assert 'id="selz_id"' in html
        assert "Selectize" in html
        assert "<select" in html

    def test_input_selectize_returns_tag(self) -> None:
        """Test that input_selectize returns a Tag."""
        result = input_selectize("selz_id", "Selectize", ["a"])
        assert isinstance(result, Tag)

    def test_input_selectize_dict_choices(self) -> None:
        """Test input_selectize with dict choices."""
        result = input_selectize(
            "selz_id", "Selectize", {"a": "Choice A", "b": "Choice B"}
        )
        html = str(result)

        assert 'value="a"' in html
        assert 'value="b"' in html
        assert "Choice A" in html
        assert "Choice B" in html

    def test_input_selectize_selected(self) -> None:
        """Test input_selectize with selected value."""
        result = input_selectize("selz_id", "Selectize", ["a", "b", "c"], selected="b")
        html = str(result)

        assert 'value="b"' in html

    def test_input_selectize_multiple_true(self) -> None:
        """Test input_selectize with multiple=True."""
        result = input_selectize("selz_id", "Selectize", ["a", "b"], multiple=True)
        html = str(result)

        assert "multiple" in html

    def test_input_selectize_with_width(self) -> None:
        """Test input_selectize with width parameter."""
        result = input_selectize("selz_id", "Selectize", ["a"], width="400px")
        html = str(result)

        assert "width:400px" in html

    def test_input_selectize_remove_button_true(self) -> None:
        """Test input_selectize with remove_button=True."""
        result = input_selectize("selz_id", "Selectize", ["a", "b"], remove_button=True)
        html = str(result)

        # Should have selectize dependencies
        assert "selz_id" in html

    def test_input_selectize_remove_button_false(self) -> None:
        """Test input_selectize with remove_button=False."""
        result = input_selectize(
            "selz_id", "Selectize", ["a", "b"], remove_button=False
        )
        html = str(result)

        assert "selz_id" in html

    def test_input_selectize_with_options(self) -> None:
        """Test input_selectize with custom options."""
        result = input_selectize(
            "selz_id",
            "Selectize",
            ["a", "b"],
            options={"placeholder": "Choose...", "maxItems": 5},
        )
        html = str(result)

        assert "application/json" in html

    def test_input_selectize_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_selectize("selz_id", "Selectize", ["a"])
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_selectize_shiny_input_select_class(self) -> None:
        """Test that select has shiny-input-select class."""
        result = input_selectize("selz_id", "Selectize", ["a"])
        html = str(result)

        assert "shiny-input-select" in html

    def test_input_selectize_html_label(self) -> None:
        """Test input_selectize with HTML label."""
        from htmltools import tags

        label = tags.em("Italic Selectize")
        result = input_selectize("selz_id", label, ["a", "b"])
        html = str(result)

        assert "<em>Italic Selectize</em>" in html

    def test_input_selectize_has_selectize_deps(self) -> None:
        """Test that input_selectize includes selectize dependencies."""
        result = input_selectize("selz_id", "Selectize", ["a"])
        html = str(result)

        # Should have script tag for selectize options
        assert "<script" in html

    def test_input_selectize_optgroup_choices(self) -> None:
        """Test input_selectize with optgroup choices."""
        result = input_selectize(
            "selz_id",
            "Selectize",
            {"Group A": {"a1": "A1"}, "Group B": {"b1": "B1"}},
        )
        html = str(result)

        assert "<optgroup" in html
        assert 'label="Group A"' in html
        assert 'label="Group B"' in html

    def test_input_selectize_selected_list(self) -> None:
        """Test input_selectize with list of selected values."""
        result = input_selectize(
            "selz_id",
            "Selectize",
            ["a", "b", "c"],
            selected=["a", "c"],
            multiple=True,
        )
        html = str(result)

        assert 'value="a"' in html
        assert 'value="c"' in html
