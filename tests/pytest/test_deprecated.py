"""Tests for shiny/_deprecated.py"""

from __future__ import annotations

import warnings

import pytest

from shiny._deprecated import (
    ShinyDeprecationWarning,
    event,
    render_image,
    render_plot,
    render_text,
    render_ui,
    warn_deprecated,
)


class TestShinyDeprecationWarning:
    """Tests for the ShinyDeprecationWarning class."""

    def test_is_runtime_warning(self) -> None:
        """Test that ShinyDeprecationWarning is a RuntimeWarning."""
        assert issubclass(ShinyDeprecationWarning, RuntimeWarning)

    def test_can_be_raised(self) -> None:
        """Test that ShinyDeprecationWarning can be raised."""
        with pytest.raises(ShinyDeprecationWarning):
            raise ShinyDeprecationWarning("test message")


class TestWarnDeprecated:
    """Tests for the warn_deprecated function."""

    def test_issues_shiny_deprecation_warning(self) -> None:
        """Test that warn_deprecated issues ShinyDeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("test deprecation message", stacklevel=1)

            assert len(w) == 1
            assert issubclass(w[0].category, ShinyDeprecationWarning)
            assert "test deprecation message" in str(w[0].message)

    def test_custom_stacklevel(self) -> None:
        """Test that warn_deprecated uses custom stacklevel."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("test message", stacklevel=2)

            assert len(w) == 1


class TestDeprecatedRenderFunctions:
    """Tests for deprecated render functions."""

    def test_render_text_shows_deprecation_warning(self) -> None:
        """Test that render_text() shows deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            decorator = render_text()

            # Check that we got a warning
            assert any(
                "render_text() is deprecated" in str(warning.message) for warning in w
            )
            # Check that we got a decorator function
            assert callable(decorator)

    def test_render_ui_shows_deprecation_warning(self) -> None:
        """Test that render_ui() shows deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            decorator = render_ui()

            # Check that we got a warning
            assert any(
                "render_ui() is deprecated" in str(warning.message) for warning in w
            )
            # Check that we got a decorator function
            assert callable(decorator)

    def test_render_plot_shows_deprecation_warning(self) -> None:
        """Test that render_plot() shows deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            decorator = render_plot()

            # Check that we got a warning
            assert any(
                "render_plot() is deprecated" in str(warning.message) for warning in w
            )
            # Check that we got a decorator function
            assert callable(decorator)

    def test_render_image_shows_deprecation_warning(self) -> None:
        """Test that render_image() shows deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            decorator = render_image()

            # Check that we got a warning
            assert any(
                "render_image() is deprecated" in str(warning.message) for warning in w
            )
            # Check that we got a decorator function
            assert callable(decorator)


class TestDeprecatedEvent:
    """Tests for deprecated event decorator."""

    def test_event_shows_deprecation_warning(self) -> None:
        """Test that event() shows deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # event() requires at least one reactive dependency
            from shiny import reactive

            rv = reactive.value(0)

            # Create event decorator with a dependency
            _ = event(rv)

            # Check that we got a warning
            assert any(
                "@event() is deprecated" in str(warning.message) for warning in w
            )


class TestDeprecatedExports:
    """Test that deprecated functions are properly exported."""

    def test_all_exports_available(self) -> None:
        """Test that all __all__ exports are available."""
        from shiny._deprecated import __all__

        expected = ("render_text", "render_plot", "render_image", "render_ui", "event")
        assert __all__ == expected
