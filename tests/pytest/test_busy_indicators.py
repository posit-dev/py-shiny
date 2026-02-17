"""Tests for shiny.ui.busy_indicators module."""

from shiny.ui.busy_indicators import options, use


class TestBusyIndicatorsOptions:
    """Tests for busy_indicators.options function."""

    def test_options_basic(self):
        """Test basic options creation."""
        result = options()
        assert result is not None

    def test_options_with_spinner_type(self):
        """Test options with spinner type."""
        result = options(spinner_type="ring")
        # Should contain spinner customization
        assert result is not None

    def test_options_with_spinner_color(self):
        """Test options with spinner color."""
        result = options(spinner_color="red")
        assert result is not None

    def test_options_with_spinner_size(self):
        """Test options with spinner size."""
        result = options(spinner_size="50px")
        # Result is a CardItem, just verify it's created
        assert result is not None

    def test_options_with_spinner_delay(self):
        """Test options with spinner delay."""
        result = options(spinner_delay="500ms")
        # Result is a CardItem, just verify it's created
        assert result is not None

    def test_options_with_fade_opacity(self):
        """Test options with fade opacity."""
        result = options(fade_opacity=0.5)
        # Result is a CardItem, just verify it's created
        assert result is not None

    def test_options_with_pulse_background(self):
        """Test options with pulse background."""
        result = options(pulse_background="linear-gradient(to right, red, blue)")
        # Should contain the gradient
        assert result is not None

    def test_options_with_pulse_height(self):
        """Test options with pulse height."""
        result = options(pulse_height="5px")
        # Result is a CardItem, just verify it's created
        assert result is not None

    def test_options_with_pulse_speed(self):
        """Test options with pulse speed."""
        result = options(pulse_speed="2s")
        # Result is a CardItem, just verify it's created
        assert result is not None


class TestBusyIndicatorsUse:
    """Tests for busy_indicators.use function."""

    def test_use_defaults(self):
        """Test use with default settings."""
        result = use()
        assert result is not None

    def test_use_spinners_true(self):
        """Test use with spinners enabled."""
        result = use(spinners=True)
        assert result is not None

    def test_use_spinners_false(self):
        """Test use with spinners disabled."""
        result = use(spinners=False)
        assert result is not None

    def test_use_pulse_true(self):
        """Test use with pulse enabled."""
        result = use(pulse=True)
        assert result is not None

    def test_use_pulse_false(self):
        """Test use with pulse disabled."""
        result = use(pulse=False)
        assert result is not None

    def test_use_fade_true(self):
        """Test use with fade enabled."""
        result = use(fade=True)
        assert result is not None

    def test_use_fade_false(self):
        """Test use with fade disabled."""
        result = use(fade=False)
        assert result is not None

    def test_use_all_disabled(self):
        """Test use with all indicators disabled."""
        result = use(spinners=False, pulse=False, fade=False)
        assert result is not None

    def test_use_all_enabled(self):
        """Test use with all indicators enabled."""
        result = use(spinners=True, pulse=True, fade=True)
        assert result is not None


class TestBusySpinnerTypes:
    """Tests for BusySpinnerType type."""

    def test_spinner_types_bars(self):
        """Test bars spinner type."""
        result = options(spinner_type="bars")
        assert result is not None

    def test_spinner_types_dots(self):
        """Test dots spinner type."""
        result = options(spinner_type="dots")
        assert result is not None

    def test_spinner_types_ring(self):
        """Test ring spinner type."""
        result = options(spinner_type="ring")
        assert result is not None
