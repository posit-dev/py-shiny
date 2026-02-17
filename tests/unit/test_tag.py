"""Tests for shiny/ui/_tag.py"""

from htmltools import div

from shiny.ui._tag import consolidate_attrs, trinary


class TestConsolidateAttrs:
    """Tests for the consolidate_attrs function."""

    def test_consolidate_attrs_kwargs_only(self):
        """Test consolidate_attrs with keyword arguments only."""
        attrs, children = consolidate_attrs(id="my-id", class_="my-class")
        assert "id" in attrs
        assert attrs["id"] == "my-id"
        assert len(children) == 0

    def test_consolidate_attrs_children_only(self):
        """Test consolidate_attrs with children only."""
        _attrs, children = consolidate_attrs("Child 1", "Child 2")
        assert len(children) == 2
        assert "Child 1" in children
        assert "Child 2" in children

    def test_consolidate_attrs_mixed(self):
        """Test consolidate_attrs with both children and attributes."""
        attrs, children = consolidate_attrs(
            "Content",
            div("Nested"),
            id="my-id",
            class_="my-class",
        )
        assert "id" in attrs
        assert attrs["id"] == "my-id"
        assert len(children) == 2

    def test_consolidate_attrs_dict_attrs(self):
        """Test consolidate_attrs with dict attributes."""
        attrs, children = consolidate_attrs(
            {"class": "dict-class"},
            "Content",
            id="my-id",
        )
        # Dict attributes should be in attrs
        assert "class" in attrs
        # Children should not include dicts
        assert len(children) == 1
        assert children[0] == "Content"

    def test_consolidate_attrs_returns_tuple(self):
        """Test consolidate_attrs returns a tuple."""
        result = consolidate_attrs("Content", id="my-id")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_consolidate_attrs_empty(self):
        """Test consolidate_attrs with no arguments."""
        attrs, children = consolidate_attrs()
        assert isinstance(attrs, dict)
        assert isinstance(children, list)
        assert len(children) == 0


class TestTrinary:
    """Tests for the trinary function."""

    def test_trinary_none(self):
        """Test trinary with None."""
        result = trinary(None)
        assert result is None

    def test_trinary_true(self):
        """Test trinary with True."""
        result = trinary(True)
        assert result == "true"

    def test_trinary_false(self):
        """Test trinary with False."""
        result = trinary(False)
        assert result == "false"

    def test_trinary_string_truthy(self):
        """Test trinary with truthy string."""
        result = trinary("yes")
        assert result == "true"

    def test_trinary_string_empty(self):
        """Test trinary with empty string (falsy)."""
        result = trinary("")
        assert result == "false"
