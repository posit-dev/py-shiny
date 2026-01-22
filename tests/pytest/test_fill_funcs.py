"""Tests for shiny.ui.fill._fill module."""

from htmltools import Tag, div

from shiny.ui.fill._fill import (
    FILL_CONTAINER_CLASS,
    FILL_ITEM_CLASS,
    as_fill_item,
    as_fillable_container,
    is_fill_item,
    is_fillable_container,
    remove_all_fill,
)


class TestAsFillableContainer:
    """Tests for as_fillable_container function."""

    def test_as_fillable_container_basic(self) -> None:
        """Test basic as_fillable_container conversion."""
        tag = div("content")
        result = as_fillable_container(tag)
        assert isinstance(result, Tag)
        assert result.has_class(FILL_CONTAINER_CLASS)

    def test_as_fillable_container_preserves_content(self) -> None:
        """Test as_fillable_container preserves content."""
        tag = div("content", id="myid")
        result = as_fillable_container(tag)
        html = str(result)
        assert "content" in html
        assert 'id="myid"' in html

    def test_as_fillable_container_creates_copy(self) -> None:
        """Test as_fillable_container creates a copy."""
        tag = div("content")
        result = as_fillable_container(tag)
        # Original tag should not be modified
        assert not tag.has_class(FILL_CONTAINER_CLASS)
        assert result.has_class(FILL_CONTAINER_CLASS)


class TestAsFillItem:
    """Tests for as_fill_item function."""

    def test_as_fill_item_basic(self) -> None:
        """Test basic as_fill_item conversion."""
        tag = div("content")
        result = as_fill_item(tag)
        assert isinstance(result, Tag)
        assert result.has_class(FILL_ITEM_CLASS)

    def test_as_fill_item_preserves_content(self) -> None:
        """Test as_fill_item preserves content."""
        tag = div("content", class_="existing")
        result = as_fill_item(tag)
        html = str(result)
        assert "content" in html
        assert "existing" in html

    def test_as_fill_item_creates_copy(self) -> None:
        """Test as_fill_item creates a copy."""
        tag = div("content")
        result = as_fill_item(tag)
        # Original tag should not be modified
        assert not tag.has_class(FILL_ITEM_CLASS)
        assert result.has_class(FILL_ITEM_CLASS)


class TestRemoveAllFill:
    """Tests for remove_all_fill function."""

    def test_remove_all_fill_removes_container(self) -> None:
        """Test remove_all_fill removes fillable container class."""
        tag = as_fillable_container(div("content"))
        assert tag.has_class(FILL_CONTAINER_CLASS)
        result = remove_all_fill(tag)
        assert not result.has_class(FILL_CONTAINER_CLASS)

    def test_remove_all_fill_removes_item(self) -> None:
        """Test remove_all_fill removes fill item class."""
        tag = as_fill_item(div("content"))
        assert tag.has_class(FILL_ITEM_CLASS)
        result = remove_all_fill(tag)
        assert not result.has_class(FILL_ITEM_CLASS)

    def test_remove_all_fill_removes_both(self) -> None:
        """Test remove_all_fill removes both container and item classes."""
        tag = as_fillable_container(div("content"))
        tag = as_fill_item(tag)
        assert tag.has_class(FILL_CONTAINER_CLASS)
        assert tag.has_class(FILL_ITEM_CLASS)
        result = remove_all_fill(tag)
        assert not result.has_class(FILL_CONTAINER_CLASS)
        assert not result.has_class(FILL_ITEM_CLASS)

    def test_remove_all_fill_creates_copy(self) -> None:
        """Test remove_all_fill creates a copy."""
        original = as_fillable_container(div("content"))
        result = remove_all_fill(original)
        # Original tag should still have the class
        assert original.has_class(FILL_CONTAINER_CLASS)
        assert not result.has_class(FILL_CONTAINER_CLASS)


class TestIsFillableContainer:
    """Tests for is_fillable_container function."""

    def test_is_fillable_container_true(self) -> None:
        """Test is_fillable_container returns True for fillable container."""
        tag = as_fillable_container(div("content"))
        assert is_fillable_container(tag) is True

    def test_is_fillable_container_false_plain_tag(self) -> None:
        """Test is_fillable_container returns False for plain tag."""
        tag = div("content")
        assert is_fillable_container(tag) is False

    def test_is_fillable_container_false_non_tag(self) -> None:
        """Test is_fillable_container returns False for non-Tag."""
        assert is_fillable_container("string") is False
        assert is_fillable_container(123) is False
        assert is_fillable_container(None) is False


class TestIsFillItem:
    """Tests for is_fill_item function."""

    def test_is_fill_item_true(self) -> None:
        """Test is_fill_item returns True for fill item."""
        tag = as_fill_item(div("content"))
        assert is_fill_item(tag) is True

    def test_is_fill_item_false_plain_tag(self) -> None:
        """Test is_fill_item returns False for plain tag."""
        tag = div("content")
        assert is_fill_item(tag) is False

    def test_is_fill_item_false_non_tag(self) -> None:
        """Test is_fill_item returns False for non-Tag."""
        assert is_fill_item("string") is False
        assert is_fill_item(123) is False
        assert is_fill_item(None) is False


class TestFillIntegration:
    """Integration tests for fill functions."""

    def test_fill_carrier(self) -> None:
        """Test creating a fill carrier (both container and item)."""
        tag = div("content")
        carrier = as_fillable_container(as_fill_item(tag))
        assert is_fill_item(carrier)
        assert is_fillable_container(carrier)

    def test_chained_operations(self) -> None:
        """Test chaining fill operations."""
        tag = div("content")
        # Add both classes
        tag = as_fill_item(tag)
        tag = as_fillable_container(tag)
        assert is_fill_item(tag)
        assert is_fillable_container(tag)
        # Remove all
        tag = remove_all_fill(tag)
        assert not is_fill_item(tag)
        assert not is_fillable_container(tag)
