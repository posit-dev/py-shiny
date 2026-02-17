"""Tests for shiny.ui.busy_indicators module."""

from htmltools import TagList

from shiny.ui import busy_indicators


class TestUseBusyIndicators:
    """Tests for busy_indicators.use function."""

    def test_use_basic(self) -> None:
        """Test basic use creation with defaults."""
        result = busy_indicators.use()
        assert isinstance(result, TagList)
        html = str(result)
        assert "shinyBusySpinners" in html
        assert "shinyBusyPulse" in html

    def test_use_with_spinners(self) -> None:
        """Test use with spinners parameter."""
        result = busy_indicators.use(spinners=True)
        html = str(result)
        assert "shinyBusySpinners" in html

    def test_use_without_spinners(self) -> None:
        """Test use without spinners."""
        result = busy_indicators.use(spinners=False)
        html = str(result)
        assert "delete document.documentElement.dataset.shinyBusySpinners" in html

    def test_use_with_pulse(self) -> None:
        """Test use with pulse parameter."""
        result = busy_indicators.use(pulse=True)
        html = str(result)
        assert "shinyBusyPulse" in html

    def test_use_without_pulse(self) -> None:
        """Test use without pulse."""
        result = busy_indicators.use(pulse=False)
        html = str(result)
        assert "delete document.documentElement.dataset.shinyBusyPulse" in html

    def test_use_both_disabled(self) -> None:
        """Test use with both disabled."""
        result = busy_indicators.use(spinners=False, pulse=False)
        html = str(result)
        assert "delete document.documentElement.dataset.shinyBusySpinners" in html
        assert "delete document.documentElement.dataset.shinyBusyPulse" in html

    def test_use_both_enabled(self) -> None:
        """Test use with both enabled."""
        result = busy_indicators.use(spinners=True, pulse=True)
        html = str(result)
        assert "shinyBusySpinners = true" in html
        assert "shinyBusyPulse = true" in html

    def test_use_with_fade_disabled(self) -> None:
        """Test use with fade disabled."""
        result = busy_indicators.use(fade=False)
        html = str(result)
        # When fade is False, should include fade_opacity=1
        assert "--shiny-fade-opacity: 1" in html


class TestBusyIndicatorsOptions:
    """Tests for busy_indicators.options function."""

    def test_options_default(self) -> None:
        """Test options with default parameters."""
        result = busy_indicators.options()
        # Should return a CardItem
        assert result is not None

    def test_options_with_spinner_color(self) -> None:
        """Test options with spinner_color."""
        result = busy_indicators.options(spinner_color="red")
        html = str(result.resolve())
        assert "--shiny-spinner-color: red" in html

    def test_options_with_spinner_size(self) -> None:
        """Test options with spinner_size."""
        result = busy_indicators.options(spinner_size="50px")
        html = str(result.resolve())
        assert "--shiny-spinner-size: 50px" in html

    def test_options_with_fade_opacity(self) -> None:
        """Test options with fade_opacity."""
        result = busy_indicators.options(fade_opacity=0.5)
        html = str(result.resolve())
        assert "--shiny-fade-opacity: 0.5" in html

    def test_options_with_spinner_delay(self) -> None:
        """Test options with spinner_delay."""
        result = busy_indicators.options(spinner_delay="500ms")
        html = str(result.resolve())
        assert "--shiny-spinner-delay: 500ms" in html

    def test_options_with_pulse_height(self) -> None:
        """Test options with pulse_height."""
        result = busy_indicators.options(pulse_height="4px")
        html = str(result.resolve())
        assert "--shiny-pulse-height: 4px" in html

    def test_options_with_pulse_speed(self) -> None:
        """Test options with pulse_speed."""
        result = busy_indicators.options(pulse_speed="1s")
        html = str(result.resolve())
        assert "--shiny-pulse-speed: 1s" in html
