"""Tests for shiny.ui._web_component module."""

from htmltools import Tag

from shiny.ui._web_component import web_component


class TestWebComponent:
    """Tests for web_component function."""

    def test_web_component_basic(self) -> None:
        """Test basic web_component creation."""
        result = web_component("my-component")
        assert isinstance(result, Tag)
        html = str(result)
        assert "my-component" in html

    def test_web_component_with_content(self) -> None:
        """Test web_component with content."""
        result = web_component("my-component", "Hello")
        html = str(result)
        assert "my-component" in html
        assert "Hello" in html

    def test_web_component_with_attributes(self) -> None:
        """Test web_component with attributes."""
        result = web_component("my-component", id="test", class_="myclass")
        html = str(result)
        assert 'id="test"' in html
        assert 'class="myclass"' in html

    def test_web_component_with_children(self) -> None:
        """Test web_component with multiple children."""
        result = web_component("my-component", "Child 1", "Child 2")
        html = str(result)
        assert "Child 1" in html
        assert "Child 2" in html

    def test_web_component_tag_name(self) -> None:
        """Test web_component returns correct tag name."""
        result = web_component("custom-element")
        assert result.name == "custom-element"

    def test_web_component_with_nested_tags(self) -> None:
        """Test web_component with nested tags."""
        inner = Tag("inner-tag", "inner content")
        result = web_component("outer-component", inner)
        html = str(result)
        assert "outer-component" in html
        assert "inner-tag" in html
        assert "inner content" in html
