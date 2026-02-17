"""Tests for shiny.ui._busy_spinner_types module."""

from typing import get_args

from shiny.ui._busy_spinner_types import BusySpinnerType


class TestBusySpinnerType:
    """Tests for BusySpinnerType literal type."""

    def test_busy_spinner_type_is_literal(self):
        """BusySpinnerType should be a Literal type."""
        # Get the allowed values from the Literal type
        allowed_values = get_args(BusySpinnerType)
        assert isinstance(allowed_values, tuple)
        assert len(allowed_values) > 0

    def test_busy_spinner_type_contains_bars_variants(self):
        """BusySpinnerType should contain bars variants."""
        allowed_values = get_args(BusySpinnerType)
        assert "bars" in allowed_values
        assert "bars2" in allowed_values
        assert "bars3" in allowed_values

    def test_busy_spinner_type_contains_dots_variants(self):
        """BusySpinnerType should contain dots variants."""
        allowed_values = get_args(BusySpinnerType)
        assert "dots" in allowed_values
        assert "dots2" in allowed_values
        assert "dots3" in allowed_values

    def test_busy_spinner_type_contains_pulse_variants(self):
        """BusySpinnerType should contain pulse variants."""
        allowed_values = get_args(BusySpinnerType)
        assert "pulse" in allowed_values
        assert "pulse2" in allowed_values
        assert "pulse3" in allowed_values

    def test_busy_spinner_type_contains_ring_variants(self):
        """BusySpinnerType should contain ring variants."""
        allowed_values = get_args(BusySpinnerType)
        assert "ring" in allowed_values
        assert "ring2" in allowed_values
        assert "ring3" in allowed_values

    def test_busy_spinner_type_has_twelve_values(self):
        """BusySpinnerType should have exactly 12 values (4 types x 3 variants each)."""
        allowed_values = get_args(BusySpinnerType)
        assert len(allowed_values) == 12

    def test_all_values_are_strings(self):
        """All BusySpinnerType values should be strings."""
        allowed_values = get_args(BusySpinnerType)
        for value in allowed_values:
            assert isinstance(value, str)
