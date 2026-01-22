"""Tests for shiny/render/_deprecated.py - Deprecated render classes."""

import pytest

from shiny._deprecated import ShinyDeprecationWarning
from shiny.render import RenderFunction, RenderFunctionAsync


class TestRenderFunction:
    """Tests for deprecated RenderFunction class."""

    def test_init_raises_deprecation_warning(self):
        """Test RenderFunction raises ShinyDeprecationWarning on init."""

        def sync_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning):
            RenderFunction(sync_fn)

    def test_deprecation_message_contains_class_name(self):
        """Test deprecation message contains class name."""

        def sync_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunction(sync_fn)

        assert "RenderFunction" in str(exc_info.value)

    def test_deprecation_message_suggests_renderer(self):
        """Test deprecation message suggests Renderer class."""

        def sync_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunction(sync_fn)

        assert "shiny.render.renderer.Renderer" in str(exc_info.value)


class TestRenderFunctionAsync:
    """Tests for deprecated RenderFunctionAsync class."""

    def test_init_raises_deprecation_warning(self):
        """Test RenderFunctionAsync raises ShinyDeprecationWarning on init."""

        async def async_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning):
            RenderFunctionAsync(async_fn)

    def test_deprecation_message_contains_class_name(self):
        """Test deprecation message contains class name."""

        async def async_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunctionAsync(async_fn)

        assert "RenderFunctionAsync" in str(exc_info.value)

    def test_deprecation_message_suggests_renderer(self):
        """Test deprecation message suggests Renderer class."""

        async def async_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunctionAsync(async_fn)

        assert "shiny.render.renderer.Renderer" in str(exc_info.value)
