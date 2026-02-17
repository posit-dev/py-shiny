"""Tests for shiny/render/renderer/_utils.py module."""

from shiny.render.renderer._utils import (
    imgdata_to_jsonifiable,
    rendered_deps_to_jsonifiable,
    set_kwargs_value,
)
from shiny.types import MISSING


class TestRenderedDepsToJsonifiable:
    """Tests for rendered_deps_to_jsonifiable function."""

    def test_rendered_deps_to_jsonifiable_is_callable(self):
        """Test rendered_deps_to_jsonifiable is callable."""
        assert callable(rendered_deps_to_jsonifiable)


class TestImgdataToJsonifiable:
    """Tests for imgdata_to_jsonifiable function."""

    def test_imgdata_to_jsonifiable_is_callable(self):
        """Test imgdata_to_jsonifiable is callable."""
        assert callable(imgdata_to_jsonifiable)


class TestSetKwargsValue:
    """Tests for set_kwargs_value function."""

    def test_set_kwargs_value_is_callable(self):
        """Test set_kwargs_value is callable."""
        assert callable(set_kwargs_value)

    def test_set_kwargs_value_with_ui_val(self):
        """Test set_kwargs_value sets ui_val when not MISSING."""
        kwargs: dict[str, str] = {}
        set_kwargs_value(kwargs, "key", "ui_value", MISSING)
        assert kwargs.get("key") == "ui_value"

    def test_set_kwargs_value_with_self_val(self):
        """Test set_kwargs_value falls back to self_val."""
        kwargs: dict[str, str] = {}
        set_kwargs_value(kwargs, "key", MISSING, "self_value")
        assert kwargs.get("key") == "self_value"

    def test_set_kwargs_value_does_nothing_with_missing(self):
        """Test set_kwargs_value does nothing when both are MISSING."""
        kwargs: dict[str, str] = {}
        set_kwargs_value(kwargs, "key", MISSING, MISSING)
        assert "key" not in kwargs
