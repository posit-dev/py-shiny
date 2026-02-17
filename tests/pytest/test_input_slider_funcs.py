"""Tests for shiny.ui._input_slider module."""

from htmltools import Tag

from shiny.ui._input_slider import input_slider


class TestInputSlider:
    """Tests for input_slider function."""

    def test_input_slider_basic(self) -> None:
        """Test basic input_slider creation."""
        result = input_slider("my_slider", "Value:", min=0, max=100, value=50)
        assert isinstance(result, Tag)

    def test_input_slider_has_id(self) -> None:
        """Test input_slider has correct id."""
        result = input_slider("slider_id", "Label", min=0, max=10, value=5)
        html = str(result)
        assert "slider_id" in html

    def test_input_slider_with_label(self) -> None:
        """Test input_slider with label."""
        result = input_slider("slider", "Choose value:", min=0, max=100, value=50)
        html = str(result)
        assert "Choose value:" in html

    def test_input_slider_with_value(self) -> None:
        """Test input_slider with initial value."""
        result = input_slider("slider", "Label", min=0, max=100, value=75)
        html = str(result)
        assert "slider" in html

    def test_input_slider_with_step(self) -> None:
        """Test input_slider with step parameter."""
        result = input_slider("slider", "Label", min=0, max=1, value=0.5, step=0.1)
        html = str(result)
        assert "slider" in html

    def test_input_slider_with_width(self) -> None:
        """Test input_slider with width parameter."""
        result = input_slider(
            "slider", "Label", min=0, max=100, value=50, width="300px"
        )
        html = str(result)
        assert "slider" in html

    def test_input_slider_range(self) -> None:
        """Test input_slider with range value (tuple)."""
        result = input_slider("slider", "Range:", min=0, max=100, value=(25, 75))
        html = str(result)
        assert "slider" in html

    def test_input_slider_animate(self) -> None:
        """Test input_slider with animate parameter."""
        result = input_slider("slider", "Label", min=0, max=100, value=0, animate=True)
        html = str(result)
        assert "slider" in html

    def test_input_slider_ticks(self) -> None:
        """Test input_slider with ticks parameter."""
        result = input_slider("slider", "Label", min=0, max=100, value=50, ticks=True)
        html = str(result)
        assert "slider" in html

    def test_input_slider_float_values(self) -> None:
        """Test input_slider with float values."""
        result = input_slider("slider", "Label", min=0.0, max=1.0, value=0.5)
        html = str(result)
        assert "slider" in html

    def test_input_slider_pre(self) -> None:
        """Test input_slider with pre parameter."""
        result = input_slider("slider", "Price:", min=0, max=100, value=50, pre="$")
        html = str(result)
        assert "slider" in html

    def test_input_slider_post(self) -> None:
        """Test input_slider with post parameter."""
        result = input_slider("slider", "Value:", min=0, max=100, value=50, post="%")
        html = str(result)
        assert "slider" in html
