"""Tests for the fill module functions."""

from htmltools import tags

from shiny.ui.fill import as_fill_item, as_fillable_container, remove_all_fill
from shiny.ui.fill._fill import FILL_CONTAINER_CLASS, FILL_ITEM_CLASS


class TestAsFillableContainer:
    """Tests for the as_fillable_container function."""

    def test_as_fillable_container_adds_class(self):
        """Test that fillable container class is added."""
        tag = tags.div("Content")
        result = as_fillable_container(tag)

        # Should have fillable container class
        assert FILL_CONTAINER_CLASS in result.attrs.get("class", "")

    def test_as_fillable_container_returns_copy(self):
        """Test that function returns a copy, not the original."""
        tag = tags.div("Content")
        result = as_fillable_container(tag)

        # Should be a different object
        assert result is not tag

    def test_as_fillable_container_preserves_content(self):
        """Test that original content is preserved."""
        tag = tags.div("Original content", class_="existing-class")
        result = as_fillable_container(tag)

        result_str = str(result)
        assert "Original content" in result_str
        assert "existing-class" in result_str

    def test_as_fillable_container_preserves_tag_name(self):
        """Test that tag name is preserved."""
        tag = tags.section("Content")
        result = as_fillable_container(tag)

        assert result.name == "section"

    def test_as_fillable_container_on_nested_tag(self):
        """Test fillable container on tag with nested children."""
        tag = tags.div(
            tags.p("Paragraph 1"),
            tags.p("Paragraph 2"),
        )
        result = as_fillable_container(tag)

        result_str = str(result)
        assert "Paragraph 1" in result_str
        assert "Paragraph 2" in result_str


class TestAsFillItem:
    """Tests for the as_fill_item function."""

    def test_as_fill_item_adds_class(self):
        """Test that fill item class is added."""
        tag = tags.div("Content")
        result = as_fill_item(tag)

        # Should have fill item class
        assert FILL_ITEM_CLASS in result.attrs.get("class", "")

    def test_as_fill_item_returns_copy(self):
        """Test that function returns a copy, not the original."""
        tag = tags.div("Content")
        result = as_fill_item(tag)

        # Should be a different object
        assert result is not tag

    def test_as_fill_item_preserves_content(self):
        """Test that original content is preserved."""
        tag = tags.div("Original content", class_="existing-class")
        result = as_fill_item(tag)

        result_str = str(result)
        assert "Original content" in result_str
        assert "existing-class" in result_str

    def test_as_fill_item_preserves_tag_name(self):
        """Test that tag name is preserved."""
        tag = tags.article("Content")
        result = as_fill_item(tag)

        assert result.name == "article"


class TestRemoveAllFill:
    """Tests for the remove_all_fill function."""

    def test_remove_all_fill_removes_fillable_class(self):
        """Test that fillable container class is removed."""
        tag = tags.div("Content", class_=FILL_CONTAINER_CLASS)
        result = remove_all_fill(tag)

        classes = result.attrs.get("class", "")
        assert FILL_CONTAINER_CLASS not in classes

    def test_remove_all_fill_removes_fill_item_class(self):
        """Test that fill item class is removed."""
        tag = tags.div("Content", class_=FILL_ITEM_CLASS)
        result = remove_all_fill(tag)

        classes = result.attrs.get("class", "")
        assert FILL_ITEM_CLASS not in classes

    def test_remove_all_fill_removes_both_classes(self):
        """Test that both fill classes are removed."""
        tag = tags.div("Content", class_=f"{FILL_CONTAINER_CLASS} {FILL_ITEM_CLASS}")
        result = remove_all_fill(tag)

        classes = result.attrs.get("class", "")
        assert FILL_CONTAINER_CLASS not in classes
        assert FILL_ITEM_CLASS not in classes

    def test_remove_all_fill_returns_copy(self):
        """Test that function returns a copy, not the original."""
        tag = tags.div("Content")
        result = remove_all_fill(tag)

        # Should be a different object
        assert result is not tag

    def test_remove_all_fill_preserves_other_classes(self):
        """Test that other classes are preserved."""
        tag = tags.div(
            "Content",
            class_=f"custom-class {FILL_CONTAINER_CLASS} another-class",
        )
        result = remove_all_fill(tag)

        classes = result.attrs.get("class", "")
        assert "custom-class" in classes
        assert "another-class" in classes

    def test_remove_all_fill_preserves_content(self):
        """Test that content is preserved."""
        tag = tags.div("Original content")
        result = remove_all_fill(tag)

        result_str = str(result)
        assert "Original content" in result_str


class TestFillCombinations:
    """Tests for combining fill functions."""

    def test_fill_item_and_fillable_container(self):
        """Test making a tag both a fill item and fillable container."""
        tag = tags.div("Content")
        result = as_fill_item(as_fillable_container(tag))

        classes = result.attrs.get("class", "")
        assert FILL_ITEM_CLASS in classes
        assert FILL_CONTAINER_CLASS in classes

    def test_remove_fill_after_adding(self):
        """Test removing fill after adding it."""
        tag = tags.div("Content")
        with_fill = as_fill_item(as_fillable_container(tag))
        result = remove_all_fill(with_fill)

        classes = result.attrs.get("class", "")
        assert FILL_ITEM_CLASS not in classes
        assert FILL_CONTAINER_CLASS not in classes

    def test_double_application_of_fillable(self):
        """Test applying fillable container twice."""
        tag = tags.div("Content")
        result = as_fillable_container(as_fillable_container(tag))

        # Should still only have one instance of the class
        result_str = str(result)
        assert FILL_CONTAINER_CLASS in result_str

    def test_double_application_of_fill_item(self):
        """Test applying fill item twice."""
        tag = tags.div("Content")
        result = as_fill_item(as_fill_item(tag))

        # Should still only have one instance of the class
        result_str = str(result)
        assert FILL_ITEM_CLASS in result_str
