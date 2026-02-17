"""Tests for shiny.ui._input_date module."""

from datetime import date

from shiny.ui import input_date, input_date_range


class TestInputDate:
    """Tests for input_date function."""

    def test_input_date_basic(self):
        """Test basic input_date creation."""
        widget = input_date("date_id", "Select Date")
        html = str(widget)
        assert "date_id" in html
        assert "Select Date" in html

    def test_input_date_with_value(self):
        """Test input_date with initial value."""
        widget = input_date("date_id", "Date", value=date(2024, 1, 15))
        html = str(widget)
        assert "2024-01-15" in html

    def test_input_date_with_string_value(self):
        """Test input_date with string value."""
        widget = input_date("date_id", "Date", value="2024-06-01")
        html = str(widget)
        assert "2024-06-01" in html

    def test_input_date_with_min_max(self):
        """Test input_date with min and max."""
        widget = input_date(
            "date_id",
            "Date",
            min=date(2024, 1, 1),
            max=date(2024, 12, 31),
        )
        html = str(widget)
        assert "date_id" in html

    def test_input_date_with_format(self):
        """Test input_date with custom format."""
        widget = input_date("date_id", "Date", format="mm/dd/yyyy")
        html = str(widget)
        assert "mm/dd/yyyy" in html

    def test_input_date_with_startview(self):
        """Test input_date with different startview."""
        widget = input_date("date_id", "Date", startview="year")
        html = str(widget)
        assert "year" in html

    def test_input_date_with_weekstart(self):
        """Test input_date with Monday as weekstart."""
        widget = input_date("date_id", "Date", weekstart=1)
        html = str(widget)
        assert "date_id" in html

    def test_input_date_with_language(self):
        """Test input_date with different language."""
        widget = input_date("date_id", "Date", language="es")
        html = str(widget)
        assert '"es"' in html

    def test_input_date_with_width(self):
        """Test input_date with width."""
        widget = input_date("date_id", "Date", width="200px")
        html = str(widget)
        assert "200px" in html

    def test_input_date_autoclose_false(self):
        """Test input_date with autoclose disabled."""
        widget = input_date("date_id", "Date", autoclose=False)
        html = str(widget)
        assert "date_id" in html


class TestInputDateRange:
    """Tests for input_date_range function."""

    def test_input_date_range_basic(self):
        """Test basic input_date_range creation."""
        widget = input_date_range("date_range", "Select Dates")
        html = str(widget)
        assert "date_range" in html
        assert "Select Dates" in html

    def test_input_date_range_with_values(self):
        """Test input_date_range with start and end values."""
        widget = input_date_range(
            "date_range",
            "Dates",
            start=date(2024, 1, 1),
            end=date(2024, 12, 31),
        )
        html = str(widget)
        assert "2024-01-01" in html
        assert "2024-12-31" in html

    def test_input_date_range_with_string_values(self):
        """Test input_date_range with string values."""
        widget = input_date_range(
            "date_range",
            "Dates",
            start="2024-06-01",
            end="2024-06-30",
        )
        html = str(widget)
        assert "2024-06-01" in html
        assert "2024-06-30" in html

    def test_input_date_range_with_min_max(self):
        """Test input_date_range with min and max."""
        widget = input_date_range(
            "date_range",
            "Dates",
            min=date(2024, 1, 1),
            max=date(2025, 12, 31),
        )
        html = str(widget)
        assert "date_range" in html

    def test_input_date_range_with_separator(self):
        """Test input_date_range with custom separator."""
        widget = input_date_range("date_range", "Dates", separator=" - ")
        html = str(widget)
        assert " - " in html

    def test_input_date_range_with_format(self):
        """Test input_date_range with custom format."""
        widget = input_date_range("date_range", "Dates", format="mm/dd/yyyy")
        html = str(widget)
        assert "mm/dd/yyyy" in html

    def test_input_date_range_with_width(self):
        """Test input_date_range with width."""
        widget = input_date_range("date_range", "Dates", width="400px")
        html = str(widget)
        assert "400px" in html
