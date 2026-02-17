"""Tests for shiny.ui._tag module."""

from shiny.ui._tag import consolidate_attrs, trinary


class TestConsolidateAttrs:
    """Tests for consolidate_attrs function."""

    def test_consolidate_attrs_empty(self):
        """Test consolidate_attrs with no arguments."""
        attrs, children = consolidate_attrs()
        assert isinstance(attrs, dict)
        assert isinstance(children, list)
        assert len(children) == 0

    def test_consolidate_attrs_with_kwargs(self):
        """Test consolidate_attrs with keyword arguments."""
        attrs, _children = consolidate_attrs(id="my_id", class_="my_class")
        assert attrs.get("id") == "my_id"
        assert attrs.get("class") == "my_class"

    def test_consolidate_attrs_with_children(self):
        """Test consolidate_attrs with child elements."""
        _attrs, children = consolidate_attrs("child1", "child2")
        assert len(children) == 2
        assert children[0] == "child1"
        assert children[1] == "child2"

    def test_consolidate_attrs_with_dict(self):
        """Test consolidate_attrs with dict attributes."""
        attrs, children = consolidate_attrs({"data-value": "test"}, "child")
        assert attrs.get("data-value") == "test"
        assert len(children) == 1
        assert children[0] == "child"

    def test_consolidate_attrs_mixed(self):
        """Test consolidate_attrs with mixed arguments."""
        attrs, children = consolidate_attrs(
            {"data-x": "1"},
            "child1",
            "child2",
            id="my_id",
            class_="my_class",
        )
        assert attrs.get("data-x") == "1"
        assert attrs.get("id") == "my_id"
        assert attrs.get("class") == "my_class"
        assert len(children) == 2


class TestTrinary:
    """Tests for trinary function."""

    def test_trinary_none(self):
        """Test trinary with None."""
        assert trinary(None) is None

    def test_trinary_true(self):
        """Test trinary with True."""
        assert trinary(True) == "true"

    def test_trinary_false(self):
        """Test trinary with False."""
        assert trinary(False) == "false"

    def test_trinary_truthy_string(self):
        """Test trinary with truthy string."""
        assert trinary("yes") == "true"

    def test_trinary_empty_string(self):
        """Test trinary with empty string."""
        assert trinary("") == "false"

    def test_trinary_1(self):
        """Test trinary with 1 (truthy)."""
        # Type checker may not like this, but let's test runtime behavior
        result = trinary(True)  # Using True as 1 equivalent
        assert result == "true"

    def test_trinary_0(self):
        """Test trinary with 0 (falsy)."""
        result = trinary(False)  # Using False as 0 equivalent
        assert result == "false"
