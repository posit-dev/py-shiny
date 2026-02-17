"""Tests for shiny/ui/fill/_fill.py"""

from htmltools import Tag, div

from shiny.ui.fill import as_fill_item, as_fillable_container, remove_all_fill


class TestAsFillableContainer:
    """Tests for the as_fillable_container function."""

    def test_basic_as_fillable_container(self):
        """Test basic fillable container conversion."""
        tag = div("Content")
        result = as_fillable_container(tag)
        html = str(result)
        assert "html-fill-container" in html

    def test_as_fillable_container_returns_tag(self):
        """Test as_fillable_container returns a Tag."""
        tag = div("Content")
        result = as_fillable_container(tag)
        assert isinstance(result, Tag)

    def test_as_fillable_container_preserves_content(self):
        """Test as_fillable_container preserves original content."""
        tag = div("Original Content", id="my-div")
        result = as_fillable_container(tag)
        html = str(result)
        assert "Original Content" in html
        assert 'id="my-div"' in html

    def test_as_fillable_container_does_not_modify_original(self):
        """Test as_fillable_container returns copy, not modifying original."""
        original = div("Content")
        original_html = str(original)
        _ = as_fillable_container(original)
        # Original should remain unchanged
        assert str(original) == original_html


class TestAsFillItem:
    """Tests for the as_fill_item function."""

    def test_basic_as_fill_item(self):
        """Test basic fill item conversion."""
        tag = div("Content")
        result = as_fill_item(tag)
        html = str(result)
        assert "html-fill-item" in html

    def test_as_fill_item_returns_tag(self):
        """Test as_fill_item returns a Tag."""
        tag = div("Content")
        result = as_fill_item(tag)
        assert isinstance(result, Tag)

    def test_as_fill_item_preserves_content(self):
        """Test as_fill_item preserves original content."""
        tag = div("Original Content", id="my-div")
        result = as_fill_item(tag)
        html = str(result)
        assert "Original Content" in html
        assert 'id="my-div"' in html

    def test_as_fill_item_does_not_modify_original(self):
        """Test as_fill_item returns copy, not modifying original."""
        original = div("Content")
        original_html = str(original)
        _ = as_fill_item(original)
        # Original should remain unchanged
        assert str(original) == original_html


class TestRemoveAllFill:
    """Tests for the remove_all_fill function."""

    def test_remove_all_fill_from_fillable(self):
        """Test removing fill from fillable container."""
        tag = div("Content")
        fillable = as_fillable_container(tag)
        result = remove_all_fill(fillable)
        html = str(result)
        assert "html-fill-container" not in html

    def test_remove_all_fill_from_fill_item(self):
        """Test removing fill from fill item."""
        tag = div("Content")
        fill_item = as_fill_item(tag)
        result = remove_all_fill(fill_item)
        html = str(result)
        assert "html-fill-item" not in html

    def test_remove_all_fill_returns_tag(self):
        """Test remove_all_fill returns a Tag."""
        tag = div("Content")
        result = remove_all_fill(tag)
        assert isinstance(result, Tag)

    def test_remove_all_fill_preserves_content(self):
        """Test remove_all_fill preserves original content."""
        tag = div("Original Content", id="my-div")
        fillable = as_fillable_container(tag)
        result = remove_all_fill(fillable)
        html = str(result)
        assert "Original Content" in html
        assert 'id="my-div"' in html

    def test_remove_all_fill_from_tag_without_fill(self):
        """Test removing fill from tag without any fill classes."""
        tag = div("Content", class_="custom-class")
        result = remove_all_fill(tag)
        html = str(result)
        assert "custom-class" in html
        assert "html-fill" not in html


class TestCombinedFillOperations:
    """Tests for combining fill operations."""

    def test_fill_item_in_fillable_container(self):
        """Test creating fill item inside fillable container."""
        inner = div("Inner Content")
        fill_item = as_fill_item(inner)
        outer = div(fill_item)
        fillable = as_fillable_container(outer)
        html = str(fillable)
        assert "html-fill-container" in html
        assert "html-fill-item" in html
        assert "Inner Content" in html

    def test_multiple_fill_conversions(self):
        """Test applying both fill item and fillable container."""
        tag = div("Content")
        result = as_fill_item(tag)
        result = as_fillable_container(result)
        html = str(result)
        assert "html-fill-item" in html
        assert "html-fill-container" in html
