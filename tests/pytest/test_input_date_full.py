"""Tests for shiny/ui/_input_date.py module."""

from shiny.ui._input_date import input_date, input_date_range


class TestInputDate:
    """Tests for input_date function."""

    def test_input_date_is_callable(self):
        """Test input_date is callable."""
        assert callable(input_date)

    def test_input_date_returns_tag(self):
        """Test input_date returns a Tag."""
        from htmltools import Tag

        result = input_date("my_date", "Select date")
        assert isinstance(result, Tag)

    def test_input_date_with_value(self):
        """Test input_date with value parameter."""
        from htmltools import Tag

        result = input_date("my_date", "Select date", value="2024-01-01")
        assert isinstance(result, Tag)

    def test_input_date_with_min_max(self):
        """Test input_date with min and max parameters."""
        from htmltools import Tag

        result = input_date(
            "my_date", "Select date", min="2024-01-01", max="2024-12-31"
        )
        assert isinstance(result, Tag)


class TestInputDateRange:
    """Tests for input_date_range function."""

    def test_input_date_range_is_callable(self):
        """Test input_date_range is callable."""
        assert callable(input_date_range)

    def test_input_date_range_returns_tag(self):
        """Test input_date_range returns a Tag."""
        from htmltools import Tag

        result = input_date_range("my_daterange", "Select dates")
        assert isinstance(result, Tag)

    def test_input_date_range_with_start_end(self):
        """Test input_date_range with start and end parameters."""
        from htmltools import Tag

        result = input_date_range(
            "my_daterange", "Select dates", start="2024-01-01", end="2024-12-31"
        )
        assert isinstance(result, Tag)


class TestInputDateExported:
    """Tests for date input functions export."""

    def test_input_date_in_ui(self):
        """Test input_date is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_date")

    def test_input_date_range_in_ui(self):
        """Test input_date_range is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_date_range")
