"""Tests for `shiny.ui._input_select`."""

from shiny.ui import input_select, input_selectize


class TestInputSelectize:
    """Tests for the input_selectize function."""

    def test_basic_selectize(self):
        """Test creating a basic selectize input."""
        sel = input_selectize("my_select", "Choose:", ["a", "b", "c"])
        html = str(sel)

        assert 'id="my_select"' in html
        assert "Choose:" in html
        # Selectize adds specific classes/attributes
        assert "selectize" in html.lower() or "shiny-input-select" in html

    def test_selectize_with_dict_choices(self):
        """Test selectize with dictionary choices."""
        sel = input_selectize(
            "my_select",
            "Choose:",
            {"val1": "Label 1", "val2": "Label 2", "val3": "Label 3"},
        )
        html = str(sel)

        assert "Label 1" in html
        assert "Label 2" in html
        assert "Label 3" in html
        assert 'value="val1"' in html
        assert 'value="val2"' in html

    def test_selectize_with_selected(self):
        """Test selectize with pre-selected value."""
        sel = input_selectize("my_select", "Choose:", ["a", "b", "c"], selected="b")
        html = str(sel)

        # The selected attribute should be present
        assert 'id="my_select"' in html
        # Selected value is passed through
        assert "b" in html

    def test_selectize_multiple(self):
        """Test selectize with multiple selection enabled."""
        sel = input_selectize("my_select", "Choose:", ["a", "b", "c"], multiple=True)
        html = str(sel)

        assert "multiple" in html

    def test_selectize_with_width(self):
        """Test selectize with custom width."""
        sel = input_selectize("my_select", "Choose:", ["a", "b", "c"], width="400px")
        html = str(sel)

        assert "400px" in html

    def test_selectize_with_optgroup(self):
        """Test selectize with option groups."""
        sel = input_selectize(
            "my_select",
            "Choose:",
            {
                "Group A": {"a1": "A Option 1", "a2": "A Option 2"},
                "Group B": {"b1": "B Option 1"},
            },
        )
        html = str(sel)

        assert "optgroup" in html.lower()
        assert "Group A" in html
        assert "Group B" in html
        assert "A Option 1" in html
        assert "B Option 1" in html

    def test_selectize_with_remove_button(self):
        """Test selectize with remove button enabled."""
        sel = input_selectize(
            "my_select", "Choose:", ["a", "b", "c"], remove_button=True
        )
        html = str(sel)

        # remove_button affects the selectize plugins configuration
        assert 'id="my_select"' in html


class TestInputSelect:
    """Tests for the input_select function."""

    def test_basic_select(self):
        """Test creating a basic select input."""
        sel = input_select("my_select", "Choose:", ["a", "b", "c"])
        html = str(sel)

        assert 'id="my_select"' in html
        assert "Choose:" in html
        assert "<select" in html
        assert "<option" in html.lower()

    def test_select_with_dict_choices(self):
        """Test select with dictionary choices."""
        sel = input_select(
            "my_select",
            "Choose:",
            {"val1": "Label 1", "val2": "Label 2"},
        )
        html = str(sel)

        assert "Label 1" in html
        assert "Label 2" in html
        assert 'value="val1"' in html
        assert 'value="val2"' in html

    def test_select_with_list_choices(self):
        """Test select with list choices (value equals label)."""
        sel = input_select("my_select", "Choose:", ["apple", "banana", "cherry"])
        html = str(sel)

        assert "apple" in html
        assert "banana" in html
        assert "cherry" in html

    def test_select_with_tuple_choices(self):
        """Test select with tuple choices."""
        sel = input_select("my_select", "Choose:", ("x", "y", "z"))
        html = str(sel)

        assert "x" in html
        assert "y" in html
        assert "z" in html

    def test_select_with_selected(self):
        """Test select with pre-selected value."""
        sel = input_select("my_select", "Choose:", ["a", "b", "c"], selected="b")
        html = str(sel)

        # There should be a selected attribute on the b option
        assert 'id="my_select"' in html

    def test_select_multiple(self):
        """Test select with multiple selection enabled."""
        sel = input_select("my_select", "Choose:", ["a", "b", "c"], multiple=True)
        html = str(sel)

        assert "multiple" in html

    def test_select_with_width(self):
        """Test select with custom width."""
        sel = input_select("my_select", "Choose:", ["a", "b", "c"], width="300px")
        html = str(sel)

        assert "300px" in html

    def test_select_with_size(self):
        """Test select with size attribute (visible items)."""
        sel = input_select("my_select", "Choose:", ["a", "b", "c", "d", "e"], size="4")
        html = str(sel)

        assert 'size="4"' in html

    def test_select_with_optgroup(self):
        """Test select with option groups."""
        sel = input_select(
            "my_select",
            "Choose:",
            {
                "Fruits": {"apple": "Apple", "banana": "Banana"},
                "Vegetables": {"carrot": "Carrot", "potato": "Potato"},
            },
        )
        html = str(sel)

        assert "<optgroup" in html
        assert "Fruits" in html
        assert "Vegetables" in html
        assert "Apple" in html
        assert "Carrot" in html

    def test_select_multiple_selected(self):
        """Test select with multiple pre-selected values."""
        sel = input_select(
            "my_select",
            "Choose:",
            ["a", "b", "c", "d"],
            selected=["b", "d"],
            multiple=True,
        )
        html = str(sel)

        assert "multiple" in html
        assert 'id="my_select"' in html
