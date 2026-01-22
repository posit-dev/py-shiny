"""Tests for shiny.ui._input_date module."""

from datetime import date

from htmltools import Tag

from shiny.ui._input_date import input_date, input_date_range


class TestInputDate:
    """Tests for input_date function."""

    def test_input_date_basic(self) -> None:
        """Test basic input_date creation."""
        result = input_date("my_date", "Select date:")
        assert isinstance(result, Tag)

    def test_input_date_has_id(self) -> None:
        """Test input_date has correct id."""
        result = input_date("date_id", "Label")
        html = str(result)
        assert "date_id" in html

    def test_input_date_with_label(self) -> None:
        """Test input_date with label."""
        result = input_date("date", "Choose a date:")
        html = str(result)
        assert "Choose a date:" in html

    def test_input_date_with_value_string(self) -> None:
        """Test input_date with string value."""
        result = input_date("date", "Label", value="2024-01-15")
        html = str(result)
        assert "2024-01-15" in html

    def test_input_date_with_value_date(self) -> None:
        """Test input_date with date value."""
        result = input_date("date", "Label", value=date(2024, 6, 15))
        html = str(result)
        assert "date" in html

    def test_input_date_with_min(self) -> None:
        """Test input_date with min parameter."""
        result = input_date("date", "Label", min="2024-01-01")
        html = str(result)
        assert "date" in html

    def test_input_date_with_max(self) -> None:
        """Test input_date with max parameter."""
        result = input_date("date", "Label", max="2024-12-31")
        html = str(result)
        assert "date" in html

    def test_input_date_with_format(self) -> None:
        """Test input_date with format parameter."""
        result = input_date("date", "Label", format="mm/dd/yyyy")
        html = str(result)
        assert "date" in html

    def test_input_date_with_startview(self) -> None:
        """Test input_date with startview parameter."""
        result = input_date("date", "Label", startview="month")
        html = str(result)
        assert "date" in html

    def test_input_date_with_weekstart(self) -> None:
        """Test input_date with weekstart parameter."""
        result = input_date("date", "Label", weekstart=1)
        html = str(result)
        assert "date" in html

    def test_input_date_with_language(self) -> None:
        """Test input_date with language parameter."""
        result = input_date("date", "Label", language="en")
        html = str(result)
        assert "date" in html

    def test_input_date_with_width(self) -> None:
        """Test input_date with width parameter."""
        result = input_date("date", "Label", width="200px")
        html = str(result)
        assert "date" in html

    def test_input_date_autoclose(self) -> None:
        """Test input_date with autoclose parameter."""
        result = input_date("date", "Label", autoclose=False)
        html = str(result)
        assert "date" in html


class TestInputDateRange:
    """Tests for input_date_range function."""

    def test_input_date_range_basic(self) -> None:
        """Test basic input_date_range creation."""
        result = input_date_range("my_date_range", "Select range:")
        assert isinstance(result, Tag)

    def test_input_date_range_has_id(self) -> None:
        """Test input_date_range has correct id."""
        result = input_date_range("date_range_id", "Label")
        html = str(result)
        assert "date_range_id" in html

    def test_input_date_range_with_label(self) -> None:
        """Test input_date_range with label."""
        result = input_date_range("date_range", "Choose date range:")
        html = str(result)
        assert "Choose date range:" in html

    def test_input_date_range_with_start(self) -> None:
        """Test input_date_range with start value."""
        result = input_date_range("date_range", "Label", start="2024-01-01")
        html = str(result)
        assert "date_range" in html

    def test_input_date_range_with_end(self) -> None:
        """Test input_date_range with end value."""
        result = input_date_range("date_range", "Label", end="2024-12-31")
        html = str(result)
        assert "date_range" in html

    def test_input_date_range_with_min(self) -> None:
        """Test input_date_range with min parameter."""
        result = input_date_range("date_range", "Label", min="2024-01-01")
        html = str(result)
        assert "date_range" in html

    def test_input_date_range_with_max(self) -> None:
        """Test input_date_range with max parameter."""
        result = input_date_range("date_range", "Label", max="2025-12-31")
        html = str(result)
        assert "date_range" in html

    def test_input_date_range_with_separator(self) -> None:
        """Test input_date_range with separator parameter."""
        result = input_date_range("date_range", "Label", separator=" to ")
        html = str(result)
        assert "date_range" in html

    def test_input_date_range_with_width(self) -> None:
        """Test input_date_range with width parameter."""
        result = input_date_range("date_range", "Label", width="300px")
        html = str(result)
        assert "date_range" in html
