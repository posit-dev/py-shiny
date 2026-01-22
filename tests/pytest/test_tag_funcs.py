"""Tests for shiny.ui._tag module."""

from shiny.ui._tag import consolidate_attrs


class TestConsolidateAttrs:
    """Tests for consolidate_attrs function."""

    def test_consolidate_attrs_empty(self) -> None:
        """Test consolidate_attrs with no attributes."""
        result = consolidate_attrs()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_consolidate_attrs_returns_tuple(self) -> None:
        """Test consolidate_attrs returns tuple of (attrs, children)."""
        result = consolidate_attrs({"class": "test-class"})
        attrs, _children = result
        assert isinstance(attrs, dict)
        assert isinstance(_children, list)

    def test_consolidate_attrs_with_dict(self) -> None:
        """Test consolidate_attrs with dict."""
        attrs, _children = consolidate_attrs({"class": "test-class"})
        assert attrs.get("class") == "test-class"

    def test_consolidate_attrs_with_kwargs(self) -> None:
        """Test consolidate_attrs with kwargs."""
        attrs, _children = consolidate_attrs(id="my-id")
        assert attrs.get("id") == "my-id"

    def test_consolidate_attrs_with_class_(self) -> None:
        """Test consolidate_attrs with class_ parameter."""
        attrs, _children = consolidate_attrs(class_="my-class")
        assert "class" in attrs

    def test_consolidate_attrs_children_empty(self) -> None:
        """Test consolidate_attrs with no children."""
        _attrs, _children = consolidate_attrs({"id": "test"})
        assert _children == []
