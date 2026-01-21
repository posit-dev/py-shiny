"""Tests for shiny/ui/_web_component.py - Web component wrapper."""

from htmltools import Tag

from shiny.ui._web_component import web_component


class TestWebComponent:
    """Tests for web_component function."""

    def test_web_component_basic(self):
        """Test basic web_component creation."""
        result = web_component("my-component")
        assert isinstance(result, Tag)
        assert result.name == "my-component"

    def test_web_component_with_children(self):
        """Test web_component with children."""
        result = web_component("my-component", "child content")
        html = str(result)
        assert "child content" in html
        assert "<my-component" in html

    def test_web_component_with_attrs(self):
        """Test web_component with attributes."""
        result = web_component("my-component", id="my-id", class_="my-class")
        html = str(result)
        assert 'id="my-id"' in html
        assert 'class="my-class"' in html

    def test_web_component_includes_dependencies(self):
        """Test web_component includes component dependencies."""
        result = web_component("my-component")
        # Dependencies should be in children
        assert len(result.children) > 0
