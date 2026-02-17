"""Tests for shiny/ui/_tag.py"""

from __future__ import annotations

from htmltools import tags

from shiny.ui._tag import consolidate_attrs, trinary


class TestConsolidateAttrs:
    """Tests for the consolidate_attrs function."""

    def test_no_args(self) -> None:
        """Test with no arguments."""
        attrs, children = consolidate_attrs()
        assert attrs == {}
        assert children == []

    def test_only_kwargs(self) -> None:
        """Test with only keyword arguments."""
        attrs, children = consolidate_attrs(id="my_id", class_="my_class")
        assert attrs["id"] == "my_id"
        assert "my_class" in str(attrs.get("class", ""))
        assert children == []

    def test_only_children(self) -> None:
        """Test with only child elements."""
        child1 = tags.div("Child 1")
        child2 = tags.span("Child 2")
        _, children = consolidate_attrs(child1, child2)
        assert len(children) == 2
        assert children[0] is child1
        assert children[1] is child2

    def test_mixed_children_and_attrs(self) -> None:
        """Test with mixed children and attributes."""
        child = tags.div("Child")
        attrs, children = consolidate_attrs(child, id="test_id")
        assert attrs["id"] == "test_id"
        assert len(children) == 1
        assert children[0] is child

    def test_dict_attrs_filtered_from_children(self) -> None:
        """Test that dict attributes are filtered from children."""
        child = tags.div("Child")
        # consolidate_attrs wraps in a div and extracts attrs
        _attrs, children = consolidate_attrs(child, id="my_id")
        # Dict should be merged into attrs, not appear in children
        assert len(children) == 1
        assert children[0] is child

    def test_string_children(self) -> None:
        """Test with string children."""
        _, children = consolidate_attrs("Hello", "World")
        assert len(children) == 2
        assert children[0] == "Hello"
        assert children[1] == "World"


class TestTrinary:
    """Tests for the trinary function."""

    def test_none_returns_none(self) -> None:
        """Test that None returns None."""
        assert trinary(None) is None

    def test_true_returns_true_string(self) -> None:
        """Test that True returns 'true' string."""
        assert trinary(True) == "true"

    def test_false_returns_false_string(self) -> None:
        """Test that False returns 'false' string."""
        assert trinary(False) == "false"

    def test_truthy_string_returns_true(self) -> None:
        """Test that truthy string returns 'true'."""
        assert trinary("yes") == "true"
        assert trinary("anything") == "true"

    def test_empty_string_returns_false(self) -> None:
        """Test that empty string returns 'false'."""
        assert trinary("") == "false"

    def test_one_returns_true(self) -> None:
        """Test that 1 returns 'true'."""
        assert trinary(1) == "true"  # type: ignore

    def test_zero_returns_false(self) -> None:
        """Test that 0 returns 'false'."""
        assert trinary(0) == "false"  # type: ignore
