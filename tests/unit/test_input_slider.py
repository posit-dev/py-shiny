"""Unit tests for shiny.ui._input_slider module."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from htmltools import Tag

from shiny.ui import input_slider
from shiny.ui._input_slider import AnimationOptions


class TestInputSlider:
    """Tests for input_slider function."""

    def test_basic_input_slider(self) -> None:
        """Test basic input_slider with required parameters."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50)
        html = str(result)

        assert 'id="slider_id"' in html
        assert "Slider" in html
        assert "js-range-slider" in html

    def test_input_slider_returns_tag(self) -> None:
        """Test that input_slider returns a Tag."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50)
        assert isinstance(result, Tag)

    def test_input_slider_data_attributes(self) -> None:
        """Test input_slider data attributes are set correctly."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50)
        html = str(result)

        assert 'data-min="0"' in html
        assert 'data-max="100"' in html
        assert 'data-from="50"' in html

    def test_input_slider_with_step(self) -> None:
        """Test input_slider with step parameter."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50, step=10)
        html = str(result)

        assert 'data-step="10"' in html

    def test_input_slider_with_float_step(self) -> None:
        """Test input_slider with float step parameter."""
        result = input_slider(
            "slider_id", "Slider", min=0.0, max=1.0, value=0.5, step=0.1
        )
        html = str(result)

        assert 'data-step="0.1"' in html

    def test_input_slider_with_ticks(self) -> None:
        """Test input_slider with ticks=True."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=50, ticks=True
        )
        html = str(result)

        assert 'data-grid="true"' in html

    def test_input_slider_without_ticks(self) -> None:
        """Test input_slider with ticks=False."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=50, ticks=False
        )
        html = str(result)

        assert 'data-grid="false"' in html

    def test_input_slider_with_width(self) -> None:
        """Test input_slider with width parameter."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=50, width="400px"
        )
        html = str(result)

        assert "width:400px" in html

    def test_input_slider_with_sep(self) -> None:
        """Test input_slider with sep parameter."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=10000, value=5000, sep=","
        )
        html = str(result)

        assert 'data-prettify-separator=","' in html

    def test_input_slider_with_pre(self) -> None:
        """Test input_slider with pre parameter."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50, pre="$")
        html = str(result)

        assert 'data-prefix="$"' in html

    def test_input_slider_with_post(self) -> None:
        """Test input_slider with post parameter."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50, post="%")
        html = str(result)

        assert 'data-postfix="%"' in html

    def test_input_slider_range(self) -> None:
        """Test input_slider with range values."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=[25, 75])
        html = str(result)

        assert 'data-from="25"' in html
        assert 'data-to="75"' in html
        assert 'data-type="double"' in html

    def test_input_slider_range_tuple(self) -> None:
        """Test input_slider with tuple range values."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=(20, 80))
        html = str(result)

        assert 'data-from="20"' in html
        assert 'data-to="80"' in html

    def test_input_slider_drag_range_true(self) -> None:
        """Test input_slider range with drag_range=True."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=[25, 75], drag_range=True
        )
        html = str(result)

        assert 'data-drag-interval="true"' in html

    def test_input_slider_drag_range_false(self) -> None:
        """Test input_slider range with drag_range=False."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=[25, 75], drag_range=False
        )
        html = str(result)

        assert 'data-drag-interval="false"' in html

    def test_input_slider_with_animate_true(self) -> None:
        """Test input_slider with animate=True."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=50, animate=True
        )
        html = str(result)

        assert "slider-animate-container" in html
        assert "slider-animate-button" in html

    def test_input_slider_with_animate_false(self) -> None:
        """Test input_slider with animate=False."""
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=50, animate=False
        )
        html = str(result)

        assert "slider-animate-container" not in html

    def test_input_slider_with_animation_options(self) -> None:
        """Test input_slider with AnimationOptions."""
        options: AnimationOptions = {
            "interval": 1000,
            "loop": True,
        }
        result = input_slider(
            "slider_id", "Slider", min=0, max=100, value=50, animate=options
        )
        html = str(result)

        assert "slider-animate-container" in html
        assert 'data-interval="1000"' in html

    def test_input_slider_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50)
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_slider_html_label(self) -> None:
        """Test input_slider with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Slider")
        result = input_slider("slider_id", label, min=0, max=100, value=50)
        html = str(result)

        assert "<strong>Bold Slider</strong>" in html

    def test_input_slider_negative_values(self) -> None:
        """Test input_slider with negative values."""
        result = input_slider("slider_id", "Slider", min=-100, max=0, value=-50)
        html = str(result)

        assert 'data-min="-100"' in html
        assert 'data-max="0"' in html
        assert 'data-from="-50"' in html

    def test_input_slider_float_values(self) -> None:
        """Test input_slider with float values."""
        result = input_slider("slider_id", "Slider", min=0.0, max=1.0, value=0.5)
        html = str(result)

        assert 'data-min="0.0"' in html
        assert 'data-max="1.0"' in html
        assert 'data-from="0.5"' in html

    def test_input_slider_date_values(self) -> None:
        """Test input_slider with date values."""
        result = input_slider(
            "slider_id",
            "Date Slider",
            min=date(2023, 1, 1),
            max=date(2023, 12, 31),
            value=date(2023, 6, 15),
        )
        html = str(result)

        assert 'data-data-type="date"' in html
        assert "js-range-slider" in html

    def test_input_slider_datetime_values(self) -> None:
        """Test input_slider with datetime values."""
        result = input_slider(
            "slider_id",
            "DateTime Slider",
            min=datetime(2023, 1, 1, 0, 0),
            max=datetime(2023, 12, 31, 23, 59),
            value=datetime(2023, 6, 15, 12, 0),
        )
        html = str(result)

        assert 'data-data-type="datetime"' in html
        assert "js-range-slider" in html

    def test_input_slider_date_with_step_timedelta(self) -> None:
        """Test input_slider with date and timedelta step."""
        result = input_slider(
            "slider_id",
            "Date Slider",
            min=date(2023, 1, 1),
            max=date(2023, 12, 31),
            value=date(2023, 6, 15),
            step=timedelta(days=7),
        )
        html = str(result)

        assert "js-range-slider" in html

    def test_input_slider_data_skin(self) -> None:
        """Test input_slider has data-skin='shiny'."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50)
        html = str(result)

        assert 'data-skin="shiny"' in html

    def test_input_slider_keyboard_enabled(self) -> None:
        """Test input_slider has keyboard support enabled."""
        result = input_slider("slider_id", "Slider", min=0, max=100, value=50)
        html = str(result)

        assert 'data-keyboard="true"' in html


class TestAnimationOptions:
    """Tests for AnimationOptions TypedDict."""

    def test_animation_options_interval(self) -> None:
        """Test AnimationOptions with interval."""
        options: AnimationOptions = {"interval": 500}
        assert options["interval"] == 500

    def test_animation_options_loop(self) -> None:
        """Test AnimationOptions with loop."""
        options: AnimationOptions = {"loop": True}
        assert options["loop"] is True

    def test_animation_options_all_fields(self) -> None:
        """Test AnimationOptions with all fields."""
        from htmltools import tags

        options: AnimationOptions = {
            "interval": 1000,
            "loop": False,
            "play_button": tags.span("Play"),
            "pause_button": tags.span("Pause"),
        }
        assert options["interval"] == 1000
        assert options["loop"] is False
        assert options["play_button"] is not None
        assert options["pause_button"] is not None
