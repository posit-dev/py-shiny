"""Tests for shiny/render/_express.py - Express render class."""

import pytest

from shiny.render import express


class TestExpressClass:
    """Tests for express render class."""

    def test_express_is_class(self):
        """Test express is a class."""
        assert isinstance(express, type)

    def test_express_is_renderer(self):
        """Test express inherits from Renderer."""
        from shiny.render.renderer import Renderer

        assert issubclass(express, Renderer)

    def test_express_callable(self):
        """Test express is callable (can be used as decorator)."""
        assert callable(express)

    def test_express_rejects_none_fn(self):
        """Test express rejects None function."""
        with pytest.raises(TypeError, match="requires a function"):
            express()(None)  # type: ignore

    def test_express_rejects_async_function(self):
        """Test express rejects async functions."""

        async def async_fn():
            return None

        with pytest.raises(TypeError, match="does not support async"):
            express()(async_fn)

    def test_express_init_defaults(self):
        """Test express initialization defaults."""

        @express
        def my_ui():
            "Hello"

        assert my_ui.inline is False
        assert my_ui.container is None
        assert my_ui.fill is False
        assert my_ui.fillable is False

    def test_express_init_with_params(self):
        """Test express initialization with parameters."""

        @express(inline=True, fill=True, fillable=True)
        def my_ui():
            "Hello"

        assert my_ui.inline is True
        assert my_ui.fill is True
        assert my_ui.fillable is True


class TestExpressAutoOutputUi:
    """Tests for express auto_output_ui method."""

    def test_auto_output_ui_returns_tag(self):
        """Test auto_output_ui returns a Tag."""
        from htmltools import Tag

        @express
        def my_ui():
            "Hello"

        my_ui._set_output_metadata(output_id="test_output")  # type: ignore
        result = my_ui.auto_output_ui()
        assert isinstance(result, Tag)

    def test_auto_output_ui_with_inline(self):
        """Test auto_output_ui with inline parameter."""
        from htmltools import Tag

        @express(inline=True)
        def my_ui():
            "Hello"

        my_ui._set_output_metadata(output_id="test_output")  # type: ignore
        result = my_ui.auto_output_ui()
        assert isinstance(result, Tag)


class TestExpressKwargsHandling:
    """Tests for express kwargs handling."""

    def test_express_accepts_kwargs(self):
        """Test express accepts additional kwargs."""

        @express(class_="custom-class")
        def my_ui():
            "Hello"

        assert my_ui.kwargs.get("class_") == "custom-class"
