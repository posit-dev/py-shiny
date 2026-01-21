"""Tests for shiny/ui/fill/_fill.py"""

from __future__ import annotations

from htmltools import tags

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
    """Tests for the as_fillable_container function."""

    def test_adds_fillable_class(self) -> None:
        """Test that it adds the fillable container class."""
        tag = tags.div("Content")
        result = as_fillable_container(tag)

        assert result.has_class(FILL_CONTAINER_CLASS)

    def test_returns_copy(self) -> None:
        """Test that it returns a copy, not modifying original."""
        tag = tags.div("Content")
        result = as_fillable_container(tag)

        # Original should not be modified
        assert not tag.has_class(FILL_CONTAINER_CLASS)
        # Result should have the class
        assert result.has_class(FILL_CONTAINER_CLASS)

    def test_preserves_existing_content(self) -> None:
        """Test that existing content is preserved."""
        tag = tags.div("Content", id="my_div")
        result = as_fillable_container(tag)

        rendered = str(result)
        assert "Content" in rendered
        assert 'id="my_div"' in rendered

    def test_with_nested_tags(self) -> None:
        """Test with nested tags."""
        tag = tags.div(tags.span("Inner"))
        result = as_fillable_container(tag)

        rendered = str(result)
        assert "Inner" in rendered
        assert FILL_CONTAINER_CLASS in rendered


class TestAsFillItem:
    """Tests for the as_fill_item function."""

    def test_adds_fill_item_class(self) -> None:
        """Test that it adds the fill item class."""
        tag = tags.div("Content")
        result = as_fill_item(tag)

        assert result.has_class(FILL_ITEM_CLASS)

    def test_returns_copy(self) -> None:
        """Test that it returns a copy, not modifying original."""
        tag = tags.div("Content")
        result = as_fill_item(tag)

        # Original should not be modified
        assert not tag.has_class(FILL_ITEM_CLASS)
        # Result should have the class
        assert result.has_class(FILL_ITEM_CLASS)

    def test_preserves_existing_content(self) -> None:
        """Test that existing content is preserved."""
        tag = tags.div("Content", class_="existing")
        result = as_fill_item(tag)

        assert result.has_class("existing")
        assert result.has_class(FILL_ITEM_CLASS)


class TestRemoveAllFill:
    """Tests for the remove_all_fill function."""

    def test_removes_fill_item_class(self) -> None:
        """Test that it removes fill item class."""
        tag = tags.div("Content", class_=FILL_ITEM_CLASS)
        result = remove_all_fill(tag)

        assert not result.has_class(FILL_ITEM_CLASS)

    def test_removes_fillable_container_class(self) -> None:
        """Test that it removes fillable container class."""
        tag = tags.div("Content", class_=FILL_CONTAINER_CLASS)
        result = remove_all_fill(tag)

        assert not result.has_class(FILL_CONTAINER_CLASS)

    def test_removes_both_classes(self) -> None:
        """Test that it removes both fill classes."""
        tag = tags.div("Content", class_=f"{FILL_ITEM_CLASS} {FILL_CONTAINER_CLASS}")
        result = remove_all_fill(tag)

        assert not result.has_class(FILL_ITEM_CLASS)
        assert not result.has_class(FILL_CONTAINER_CLASS)

    def test_returns_copy(self) -> None:
        """Test that it returns a copy."""
        tag = tags.div("Content", class_=FILL_ITEM_CLASS)
        result = remove_all_fill(tag)

        # Original should still have the class
        assert tag.has_class(FILL_ITEM_CLASS)
        # Result should not
        assert not result.has_class(FILL_ITEM_CLASS)

    def test_preserves_other_classes(self) -> None:
        """Test that it preserves other classes."""
        tag = tags.div("Content", class_=f"my-class {FILL_ITEM_CLASS}")
        result = remove_all_fill(tag)

        assert result.has_class("my-class")
        assert not result.has_class(FILL_ITEM_CLASS)


class TestIsFillableContainer:
    """Tests for the is_fillable_container function."""

    def test_tag_with_fillable_class(self) -> None:
        """Test that tag with fillable class returns True."""
        tag = tags.div(class_=FILL_CONTAINER_CLASS)
        assert is_fillable_container(tag) is True

    def test_tag_without_fillable_class(self) -> None:
        """Test that tag without fillable class returns False."""
        tag = tags.div()
        assert is_fillable_container(tag) is False

    def test_non_tag_returns_false(self) -> None:
        """Test that non-Tag returns False."""
        assert is_fillable_container("string") is False
        assert is_fillable_container(123) is False
        assert is_fillable_container(None) is False

    def test_as_fillable_container_result(self) -> None:
        """Test result of as_fillable_container is recognized."""
        tag = as_fillable_container(tags.div())
        assert is_fillable_container(tag) is True


class TestIsFillItem:
    """Tests for the is_fill_item function."""

    def test_tag_with_fill_item_class(self) -> None:
        """Test that tag with fill item class returns True."""
        tag = tags.div(class_=FILL_ITEM_CLASS)
        assert is_fill_item(tag) is True

    def test_tag_without_fill_item_class(self) -> None:
        """Test that tag without fill item class returns False."""
        tag = tags.div()
        assert is_fill_item(tag) is False

    def test_non_tag_returns_false(self) -> None:
        """Test that non-Tag returns False."""
        assert is_fill_item("string") is False
        assert is_fill_item(123) is False
        assert is_fill_item(None) is False

    def test_as_fill_item_result(self) -> None:
        """Test result of as_fill_item is recognized."""
        tag = as_fill_item(tags.div())
        assert is_fill_item(tag) is True


class TestFillConstants:
    """Tests for fill-related constants."""

    def test_fill_item_class_value(self) -> None:
        """Test FILL_ITEM_CLASS constant value."""
        assert FILL_ITEM_CLASS == "html-fill-item"

    def test_fill_container_class_value(self) -> None:
        """Test FILL_CONTAINER_CLASS constant value."""
        assert FILL_CONTAINER_CLASS == "html-fill-container"
