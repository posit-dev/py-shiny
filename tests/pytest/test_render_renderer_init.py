"""Tests for shiny/render/renderer/__init__.py - Renderer module exports."""

from shiny.render import renderer


class TestRendererExports:
    """Tests for renderer module exports."""

    def test_renderer_exported(self):
        """Test Renderer is exported."""
        assert hasattr(renderer, "Renderer")

    def test_valuefn_exported(self):
        """Test ValueFn is exported."""
        assert hasattr(renderer, "ValueFn")

    def test_jsonifiable_exported(self):
        """Test Jsonifiable is exported."""
        assert hasattr(renderer, "Jsonifiable")

    def test_asyncvaluefn_exported(self):
        """Test AsyncValueFn is exported."""
        assert hasattr(renderer, "AsyncValueFn")

    def test_renderert_exported(self):
        """Test RendererT is exported."""
        assert hasattr(renderer, "RendererT")


class TestRendererAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(renderer.__all__, tuple)

    def test_all_contains_renderer(self):
        """Test __all__ contains Renderer."""
        assert "Renderer" in renderer.__all__

    def test_all_contains_valuefn(self):
        """Test __all__ contains ValueFn."""
        assert "ValueFn" in renderer.__all__

    def test_all_contains_jsonifiable(self):
        """Test __all__ contains Jsonifiable."""
        assert "Jsonifiable" in renderer.__all__

    def test_all_contains_asyncvaluefn(self):
        """Test __all__ contains AsyncValueFn."""
        assert "AsyncValueFn" in renderer.__all__

    def test_all_contains_renderert(self):
        """Test __all__ contains RendererT."""
        assert "RendererT" in renderer.__all__
