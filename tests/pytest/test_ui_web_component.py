"""Tests for shiny/ui/_web_component.py - Web component helper."""

from htmltools import Tag

from shiny.ui._web_component import web_component


class TestWebComponent:
    """Tests for web_component function."""

    def test_web_component_returns_tag(self):
        """Test web_component returns a Tag."""
        result = web_component("custom-element")
        assert isinstance(result, Tag)

    def test_web_component_has_correct_tag_name(self):
        """Test web_component has correct tag name."""
        result = web_component("my-component")
        assert result.name == "my-component"

    def test_web_component_with_children(self):
        """Test web_component with children."""
        result = web_component("custom-element", "child text")
        html = str(result)
        assert "child text" in html

    def test_web_component_with_attributes(self):
        """Test web_component with attributes."""
        result = web_component("custom-element", id="my-id", data_value="test")
        assert result.attrs.get("id") == "my-id"

    def test_web_component_includes_dependencies(self):
        """Test web_component includes component dependencies."""
        result = web_component("custom-element")
        # Should have dependencies in children
        assert len(result.children) > 0

    def test_web_component_multiple_children(self):
        """Test web_component with multiple children."""
        from htmltools import div

        result = web_component("custom-element", "text", div("child"))
        html = str(result)
        assert "text" in html
        assert "<div>" in html

    def test_web_component_nested(self):
        """Test nested web components."""
        inner = web_component("inner-component", "inner")
        outer = web_component("outer-component", inner)
        html = str(outer)
        assert "inner-component" in html
        assert "outer-component" in html
