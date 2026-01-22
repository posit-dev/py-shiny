"""Tests for fill module."""

from htmltools import tags
from shiny.ui.fill import (
    as_fillable_container,
    as_fill_item,
    remove_all_fill,
)


class TestAsFillableContainer:
    """Tests for as_fillable_container function."""

    def test_basic_fillable_container(self):
        """Test making a tag a fillable container."""
        div = tags.div("Content")
        fillable = as_fillable_container(div)
        html = str(fillable)

        assert "html-fill-container" in html

    def test_fillable_container_preserves_content(self):
        """Test that content is preserved."""
        div = tags.div("My Content")
        fillable = as_fillable_container(div)
        html = str(fillable)

        assert "My Content" in html

    def test_fillable_container_original_unchanged(self):
        """Test that original tag is not modified."""
        div = tags.div("Content")
        original_html = str(div)
        _ = as_fillable_container(div)

        # Original should not have the fill class
        assert str(div) == original_html


class TestAsFillItem:
    """Tests for as_fill_item function."""

    def test_basic_fill_item(self):
        """Test making a tag a fill item."""
        div = tags.div("Content")
        fill = as_fill_item(div)
        html = str(fill)

        assert "html-fill-item" in html

    def test_fill_item_preserves_content(self):
        """Test that content is preserved."""
        div = tags.div("My Content")
        fill = as_fill_item(div)
        html = str(fill)

        assert "My Content" in html

    def test_fill_item_original_unchanged(self):
        """Test that original tag is not modified."""
        div = tags.div("Content")
        original_html = str(div)
        _ = as_fill_item(div)

        # Original should not have the fill class
        assert str(div) == original_html


class TestRemoveAllFill:
    """Tests for remove_all_fill function."""

    def test_remove_fill_from_fillable_container(self):
        """Test removing fill classes from a fillable container."""
        div = tags.div("Content")
        fillable = as_fillable_container(div)
        cleaned = remove_all_fill(fillable)
        html = str(cleaned)

        assert "html-fill-container" not in html

    def test_remove_fill_from_fill_item(self):
        """Test removing fill classes from a fill item."""
        div = tags.div("Content")
        fill = as_fill_item(div)
        cleaned = remove_all_fill(fill)
        html = str(cleaned)

        assert "html-fill-item" not in html

    def test_remove_fill_from_combined(self):
        """Test removing fill classes from a tag that is both."""
        div = tags.div("Content")
        combined = as_fill_item(as_fillable_container(div))
        cleaned = remove_all_fill(combined)
        html = str(cleaned)

        assert "html-fill-container" not in html
        assert "html-fill-item" not in html

    def test_remove_fill_preserves_content(self):
        """Test that content is preserved when removing fill."""
        div = tags.div("Important Content")
        fillable = as_fillable_container(div)
        cleaned = remove_all_fill(fillable)
        html = str(cleaned)

        assert "Important Content" in html

    def test_remove_fill_from_regular_tag(self):
        """Test remove_all_fill on a tag without fill classes."""
        div = tags.div("Content", class_="my-class")
        cleaned = remove_all_fill(div)
        html = str(cleaned)

        # Should still have original class
        assert "my-class" in html
        assert "Content" in html
