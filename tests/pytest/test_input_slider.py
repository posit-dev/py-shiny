"""Tests for shiny.ui._input_slider module."""

from datetime import date, datetime, timedelta

from shiny.ui import input_slider
from shiny.ui._input_slider import AnimationOptions


class TestInputSlider:
    """Tests for the input_slider function."""

    def test_basic_slider(self):
        """Test creating a basic slider with numeric values."""
        result = input_slider("slider1", "Slider:", min=0, max=100, value=50)
        html = str(result)

        assert 'id="slider1"' in html
        assert "Slider:" in html
        assert "js-range-slider" in html or "shiny-input-slider" in html

    def test_slider_with_step(self):
        """Test slider with custom step value."""
        result = input_slider(
            "slider2", "Step slider:", min=0, max=10, value=5, step=0.5
        )
        html = str(result)

        assert 'id="slider2"' in html

    def test_slider_range(self):
        """Test slider with range (two values)."""
        result = input_slider("slider3", "Range:", min=0, max=100, value=[25, 75])
        html = str(result)

        assert 'id="slider3"' in html

    def test_slider_with_width(self):
        """Test slider with custom width."""
        result = input_slider(
            "slider4", "Width slider:", min=0, max=100, value=50, width="400px"
        )
        html = str(result)

        assert "400px" in html

    def test_slider_with_ticks(self):
        """Test slider with tick marks."""
        result = input_slider(
            "slider5", "Ticks slider:", min=0, max=100, value=50, ticks=True
        )
        html = str(result)

        assert 'id="slider5"' in html

    def test_slider_with_pre_post(self):
        """Test slider with prefix and suffix."""
        result = input_slider(
            "slider6", "Price:", min=0, max=100, value=50, pre="$", post=" USD"
        )
        html = str(result)

        assert 'id="slider6"' in html
        assert "$" in html or "data-pre" in html

    def test_slider_with_sep(self):
        """Test slider with thousand separator."""
        result = input_slider(
            "slider7", "Large number:", min=0, max=1000000, value=500000, sep=","
        )
        html = str(result)

        assert 'id="slider7"' in html

    def test_slider_no_drag_range(self):
        """Test range slider with drag_range disabled."""
        result = input_slider(
            "slider8", "No drag:", min=0, max=100, value=[25, 75], drag_range=False
        )
        html = str(result)

        assert 'id="slider8"' in html

    def test_slider_with_date_values(self):
        """Test slider with date values."""
        result = input_slider(
            "slider9",
            "Date:",
            min=date(2020, 1, 1),
            max=date(2020, 12, 31),
            value=date(2020, 6, 15),
        )
        html = str(result)

        assert 'id="slider9"' in html

    def test_slider_with_datetime_values(self):
        """Test slider with datetime values."""
        result = input_slider(
            "slider10",
            "DateTime:",
            min=datetime(2020, 1, 1, 0, 0),
            max=datetime(2020, 12, 31, 23, 59),
            value=datetime(2020, 6, 15, 12, 0),
        )
        html = str(result)

        assert 'id="slider10"' in html

    def test_slider_with_datetime_step(self):
        """Test slider with timedelta step."""
        result = input_slider(
            "slider11",
            "DateTime Step:",
            min=datetime(2020, 1, 1, 0, 0),
            max=datetime(2020, 1, 1, 23, 59),
            value=datetime(2020, 1, 1, 12, 0),
            step=timedelta(hours=1),
        )
        html = str(result)

        assert 'id="slider11"' in html

    def test_slider_with_animate_true(self):
        """Test slider with animation enabled."""
        result = input_slider(
            "slider12", "Animate:", min=0, max=100, value=0, animate=True
        )
        html = str(result)

        assert 'id="slider12"' in html

    def test_slider_with_animate_options(self):
        """Test slider with custom animation options."""
        anim_opts: AnimationOptions = {
            "interval": 500,
            "loop": True,
        }
        result = input_slider(
            "slider13", "Animate Options:", min=0, max=100, value=0, animate=anim_opts
        )
        html = str(result)

        assert 'id="slider13"' in html

    def test_slider_with_time_format(self):
        """Test slider with custom time format."""
        result = input_slider(
            "slider14",
            "Formatted Date:",
            min=date(2020, 1, 1),
            max=date(2020, 12, 31),
            value=date(2020, 6, 15),
            time_format="%Y-%m-%d",
        )
        html = str(result)

        assert 'id="slider14"' in html


class TestAnimationOptions:
    """Tests for AnimationOptions TypedDict."""

    def test_animation_options_creation(self):
        """Test creating AnimationOptions."""
        opts: AnimationOptions = {
            "interval": 1000,
            "loop": True,
        }

        assert opts["interval"] == 1000
        assert opts["loop"] is True

    def test_animation_options_with_play_pause(self):
        """Test AnimationOptions with custom play/pause buttons."""
        opts: AnimationOptions = {
            "interval": 500,
            "loop": False,
            "play_button": "Play",
            "pause_button": "Pause",
        }

        assert opts["play_button"] == "Play"
        assert opts["pause_button"] == "Pause"
