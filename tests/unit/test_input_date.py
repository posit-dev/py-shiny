"""Unit tests for shiny.ui._input_date module."""

from __future__ import annotations

from datetime import date

from htmltools import Tag

from shiny.ui import input_date, input_date_range


class TestInputDate:
    """Tests for input_date function."""

    def test_basic_input_date(self) -> None:
        """Test basic input_date with required parameters."""
        result = input_date("date_id", "Select Date")
        html = str(result)

        assert 'id="date_id"' in html
        assert "Select Date" in html
        assert "shiny-date-input" in html

    def test_input_date_returns_tag(self) -> None:
        """Test that input_date returns a Tag."""
        result = input_date("date_id", "Date")
        assert isinstance(result, Tag)

    def test_input_date_with_value_date_obj(self) -> None:
        """Test input_date with date object value."""
        result = input_date("date_id", "Date", value=date(2023, 6, 15))
        html = str(result)

        assert "2023-06-15" in html

    def test_input_date_with_value_string(self) -> None:
        """Test input_date with string value."""
        result = input_date("date_id", "Date", value="2023-12-25")
        html = str(result)

        assert "2023-12-25" in html

    def test_input_date_with_min(self) -> None:
        """Test input_date with min parameter."""
        result = input_date("date_id", "Date", min="2023-01-01")
        html = str(result)

        assert "2023-01-01" in html

    def test_input_date_with_max(self) -> None:
        """Test input_date with max parameter."""
        result = input_date("date_id", "Date", max="2024-12-31")
        html = str(result)

        assert "2024-12-31" in html

    def test_input_date_with_min_date_obj(self) -> None:
        """Test input_date with min as date object."""
        result = input_date("date_id", "Date", min=date(2023, 1, 1))
        html = str(result)

        assert "2023-01-01" in html

    def test_input_date_with_max_date_obj(self) -> None:
        """Test input_date with max as date object."""
        result = input_date("date_id", "Date", max=date(2024, 12, 31))
        html = str(result)

        assert "2024-12-31" in html

    def test_input_date_with_format(self) -> None:
        """Test input_date with custom format."""
        result = input_date("date_id", "Date", format="mm/dd/yyyy")
        html = str(result)

        assert 'data-date-format="mm/dd/yyyy"' in html

    def test_input_date_default_format(self) -> None:
        """Test input_date default format."""
        result = input_date("date_id", "Date")
        html = str(result)

        assert 'data-date-format="yyyy-mm-dd"' in html

    def test_input_date_with_startview_month(self) -> None:
        """Test input_date with startview='month'."""
        result = input_date("date_id", "Date", startview="month")
        html = str(result)

        assert 'data-date-start-view="month"' in html

    def test_input_date_with_startview_year(self) -> None:
        """Test input_date with startview='year'."""
        result = input_date("date_id", "Date", startview="year")
        html = str(result)

        assert 'data-date-start-view="year"' in html

    def test_input_date_with_startview_decade(self) -> None:
        """Test input_date with startview='decade'."""
        result = input_date("date_id", "Date", startview="decade")
        html = str(result)

        assert 'data-date-start-view="decade"' in html

    def test_input_date_with_weekstart(self) -> None:
        """Test input_date with weekstart parameter."""
        result = input_date("date_id", "Date", weekstart=1)
        html = str(result)

        assert 'data-date-week-start="1"' in html

    def test_input_date_with_language(self) -> None:
        """Test input_date with language parameter."""
        result = input_date("date_id", "Date", language="fr")
        html = str(result)

        assert 'data-date-language="fr"' in html

    def test_input_date_default_language(self) -> None:
        """Test input_date default language is 'en'."""
        result = input_date("date_id", "Date")
        html = str(result)

        assert 'data-date-language="en"' in html

    def test_input_date_with_width(self) -> None:
        """Test input_date with width parameter."""
        result = input_date("date_id", "Date", width="300px")
        html = str(result)

        assert "width:300px" in html

    def test_input_date_with_autoclose_true(self) -> None:
        """Test input_date with autoclose=True."""
        result = input_date("date_id", "Date", autoclose=True)
        html = str(result)

        assert 'data-date-autoclose="true"' in html

    def test_input_date_with_autoclose_false(self) -> None:
        """Test input_date with autoclose=False."""
        result = input_date("date_id", "Date", autoclose=False)
        html = str(result)

        assert 'data-date-autoclose="false"' in html

    def test_input_date_with_datesdisabled(self) -> None:
        """Test input_date with datesdisabled parameter."""
        result = input_date(
            "date_id",
            "Date",
            datesdisabled=["2023-12-25", "2023-12-26"],
        )
        html = str(result)

        assert "2023-12-25" in html
        assert "2023-12-26" in html

    def test_input_date_with_daysofweekdisabled(self) -> None:
        """Test input_date with daysofweekdisabled parameter."""
        result = input_date("date_id", "Date", daysofweekdisabled=[0, 6])
        html = str(result)

        assert "data-date-days-of-week-disabled" in html

    def test_input_date_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_date("date_id", "Date")
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_date_html_label(self) -> None:
        """Test input_date with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Date")
        result = input_date("date_id", label)
        html = str(result)

        assert "<strong>Bold Date</strong>" in html


class TestInputDateRange:
    """Tests for input_date_range function."""

    def test_basic_input_date_range(self) -> None:
        """Test basic input_date_range with required parameters."""
        result = input_date_range("dr_id", "Select Dates")
        html = str(result)

        assert 'id="dr_id"' in html
        assert "Select Dates" in html
        assert "shiny-date-range-input" in html

    def test_input_date_range_returns_tag(self) -> None:
        """Test that input_date_range returns a Tag."""
        result = input_date_range("dr_id", "Dates")
        assert isinstance(result, Tag)

    def test_input_date_range_with_start_date_obj(self) -> None:
        """Test input_date_range with start as date object."""
        result = input_date_range("dr_id", "Dates", start=date(2023, 1, 1))
        html = str(result)

        assert "2023-01-01" in html

    def test_input_date_range_with_start_string(self) -> None:
        """Test input_date_range with start as string."""
        result = input_date_range("dr_id", "Dates", start="2023-01-01")
        html = str(result)

        assert "2023-01-01" in html

    def test_input_date_range_with_end_date_obj(self) -> None:
        """Test input_date_range with end as date object."""
        result = input_date_range("dr_id", "Dates", end=date(2023, 12, 31))
        html = str(result)

        assert "2023-12-31" in html

    def test_input_date_range_with_end_string(self) -> None:
        """Test input_date_range with end as string."""
        result = input_date_range("dr_id", "Dates", end="2023-12-31")
        html = str(result)

        assert "2023-12-31" in html

    def test_input_date_range_with_min(self) -> None:
        """Test input_date_range with min parameter."""
        result = input_date_range("dr_id", "Dates", min="2020-01-01")
        html = str(result)

        assert "2020-01-01" in html

    def test_input_date_range_with_max(self) -> None:
        """Test input_date_range with max parameter."""
        result = input_date_range("dr_id", "Dates", max="2025-12-31")
        html = str(result)

        assert "2025-12-31" in html

    def test_input_date_range_with_format(self) -> None:
        """Test input_date_range with custom format."""
        result = input_date_range("dr_id", "Dates", format="dd/mm/yyyy")
        html = str(result)

        assert 'data-date-format="dd/mm/yyyy"' in html

    def test_input_date_range_with_startview(self) -> None:
        """Test input_date_range with startview parameter."""
        result = input_date_range("dr_id", "Dates", startview="year")
        html = str(result)

        assert 'data-date-start-view="year"' in html

    def test_input_date_range_with_weekstart(self) -> None:
        """Test input_date_range with weekstart parameter."""
        result = input_date_range("dr_id", "Dates", weekstart=1)
        html = str(result)

        assert 'data-date-week-start="1"' in html

    def test_input_date_range_with_language(self) -> None:
        """Test input_date_range with language parameter."""
        result = input_date_range("dr_id", "Dates", language="de")
        html = str(result)

        assert 'data-date-language="de"' in html

    def test_input_date_range_with_separator(self) -> None:
        """Test input_date_range with custom separator."""
        result = input_date_range("dr_id", "Dates", separator=" - ")
        html = str(result)

        assert " - " in html

    def test_input_date_range_default_separator(self) -> None:
        """Test input_date_range default separator is ' to '."""
        result = input_date_range("dr_id", "Dates")
        html = str(result)

        assert " to " in html

    def test_input_date_range_with_width(self) -> None:
        """Test input_date_range with width parameter."""
        result = input_date_range("dr_id", "Dates", width="400px")
        html = str(result)

        assert "width:400px" in html

    def test_input_date_range_with_autoclose_true(self) -> None:
        """Test input_date_range with autoclose=True."""
        result = input_date_range("dr_id", "Dates", autoclose=True)
        html = str(result)

        assert 'data-date-autoclose="true"' in html

    def test_input_date_range_with_autoclose_false(self) -> None:
        """Test input_date_range with autoclose=False."""
        result = input_date_range("dr_id", "Dates", autoclose=False)
        html = str(result)

        assert 'data-date-autoclose="false"' in html

    def test_input_date_range_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_date_range("dr_id", "Dates")
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_date_range_html_label(self) -> None:
        """Test input_date_range with HTML label."""
        from htmltools import tags

        label = tags.em("Italic Dates")
        result = input_date_range("dr_id", label)
        html = str(result)

        assert "<em>Italic Dates</em>" in html

    def test_input_date_range_with_all_parameters(self) -> None:
        """Test input_date_range with all parameters."""
        result = input_date_range(
            "full_dr_id",
            "Full Date Range",
            start="2023-06-01",
            end="2023-06-30",
            min="2023-01-01",
            max="2023-12-31",
            format="mm/dd/yyyy",
            startview="month",
            weekstart=0,
            language="en",
            separator=" - ",
            width="500px",
            autoclose=True,
        )
        html = str(result)

        assert 'id="full_dr_id"' in html
        assert "Full Date Range" in html
        assert "2023-06-01" in html
        assert "2023-06-30" in html
        assert 'data-date-format="mm/dd/yyyy"' in html
        assert " - " in html
        assert "width:500px" in html
