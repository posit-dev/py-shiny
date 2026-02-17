"""Comprehensive tests for shiny.render._deprecated module."""

import pytest


class TestRenderFunctionDeprecated:
    """Tests for deprecated RenderFunction class."""

    def test_render_function_raises_deprecation_warning(self):
        """RenderFunction should raise ShinyDeprecationWarning on instantiation."""
        from shiny._deprecated import ShinyDeprecationWarning
        from shiny.render._deprecated import RenderFunction

        def dummy_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunction(dummy_fn)

        assert "RenderFunction" in str(exc_info.value)
        assert "deprecated" in str(exc_info.value).lower()
        assert "shiny.render.renderer.Renderer" in str(exc_info.value)

    def test_render_function_message_includes_class_name(self):
        """Error message should include the class name."""
        from shiny._deprecated import ShinyDeprecationWarning
        from shiny.render._deprecated import RenderFunction

        def dummy_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunction(dummy_fn)

        error_message = str(exc_info.value)
        assert "RenderFunction" in error_message


class TestRenderFunctionAsyncDeprecated:
    """Tests for deprecated RenderFunctionAsync class."""

    def test_render_function_async_raises_deprecation_warning(self):
        """RenderFunctionAsync should raise ShinyDeprecationWarning on instantiation."""
        from shiny._deprecated import ShinyDeprecationWarning
        from shiny.render._deprecated import RenderFunctionAsync

        async def dummy_async_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunctionAsync(dummy_async_fn)

        assert "RenderFunctionAsync" in str(exc_info.value)
        assert "deprecated" in str(exc_info.value).lower()
        assert "shiny.render.renderer.Renderer" in str(exc_info.value)

    def test_render_function_async_message_includes_class_name(self):
        """Error message should include the class name."""
        from shiny._deprecated import ShinyDeprecationWarning
        from shiny.render._deprecated import RenderFunctionAsync

        async def dummy_async_fn():
            return "test"

        with pytest.raises(ShinyDeprecationWarning) as exc_info:
            RenderFunctionAsync(dummy_async_fn)

        error_message = str(exc_info.value)
        assert "RenderFunctionAsync" in error_message


class TestModuleStructure:
    """Tests for module structure and exports."""

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.render._deprecated as deprecated_module

        assert deprecated_module is not None

    def test_generic_types_imported(self):
        """Module should use Generic types correctly."""
        from shiny.render._deprecated import RenderFunction, RenderFunctionAsync

        # Both classes should be generic
        assert hasattr(RenderFunction, "__orig_bases__")
        assert hasattr(RenderFunctionAsync, "__orig_bases__")
