"""Tests for shiny/ui/_input_slider.py module."""

from shiny.ui._input_slider import SliderValueArg, input_slider


class TestInputSlider:
    """Tests for input_slider function."""

    def test_input_slider_is_callable(self):
        """Test input_slider is callable."""
        assert callable(input_slider)

    def test_input_slider_returns_tag(self):
        """Test input_slider returns a Tag."""
        from htmltools import Tag

        result = input_slider("my_slider", "Slide me", min=0, max=100, value=50)
        assert isinstance(result, Tag)

    def test_input_slider_with_step(self):
        """Test input_slider with step parameter."""
        from htmltools import Tag

        result = input_slider("my_slider", "Slide me", min=0, max=100, value=50, step=5)
        assert isinstance(result, Tag)

    def test_input_slider_with_range(self):
        """Test input_slider with range value (tuple)."""
        from htmltools import Tag

        result = input_slider("my_slider", "Range", min=0, max=100, value=(25, 75))
        assert isinstance(result, Tag)


class TestSliderValueArg:
    """Tests for SliderValueArg type."""

    def test_slider_value_arg_exists(self):
        """Test SliderValueArg type exists."""
        assert SliderValueArg is not None


class TestInputSliderExported:
    """Tests for slider functions export."""

    def test_input_slider_in_ui(self):
        """Test input_slider is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_slider")
