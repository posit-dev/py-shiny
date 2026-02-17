"""Tests for shiny._deprecated module."""

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
    """Tests for ShinyDeprecationWarning class."""

    def test_is_runtime_warning(self) -> None:
        """Test ShinyDeprecationWarning is a RuntimeWarning."""
        assert issubclass(ShinyDeprecationWarning, RuntimeWarning)

    def test_can_raise(self) -> None:
        """Test ShinyDeprecationWarning can be raised."""
        with pytest.raises(ShinyDeprecationWarning):
            raise ShinyDeprecationWarning("test")


class TestWarnDeprecated:
    """Tests for warn_deprecated function."""

    def test_warn_deprecated_emits_warning(self) -> None:
        """Test warn_deprecated emits ShinyDeprecationWarning."""
        with pytest.warns(ShinyDeprecationWarning, match="test message"):
            warn_deprecated("test message")

    def test_warn_deprecated_message(self) -> None:
        """Test warn_deprecated includes custom message."""
        with pytest.warns(ShinyDeprecationWarning) as record:
            warn_deprecated("custom warning")
        assert len(record) == 1
        assert "custom warning" in str(record[0].message)


class TestDeprecatedRenderFunctions:
    """Tests for deprecated render functions."""

    def test_render_text_warns(self) -> None:
        """Test render_text emits deprecation warning."""
        with pytest.warns(ShinyDeprecationWarning, match="render_text.*deprecated"):
            render_text()

    def test_render_ui_warns(self) -> None:
        """Test render_ui emits deprecation warning."""
        with pytest.warns(ShinyDeprecationWarning, match="render_ui.*deprecated"):
            render_ui()

    def test_render_plot_warns(self) -> None:
        """Test render_plot emits deprecation warning."""
        with pytest.warns(ShinyDeprecationWarning, match="render_plot.*deprecated"):
            render_plot()

    def test_render_image_warns(self) -> None:
        """Test render_image emits deprecation warning."""
        with pytest.warns(ShinyDeprecationWarning, match="render_image.*deprecated"):
            render_image()


class TestDeprecatedEvent:
    """Tests for deprecated event decorator."""

    def test_event_warns(self) -> None:
        """Test event emits deprecation warning."""
        from shiny import reactive

        r = reactive.value(0)
        with pytest.warns(ShinyDeprecationWarning, match="@event.*deprecated"):

            @event(r)
            def my_func():
                return "test"
