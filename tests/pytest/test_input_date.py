"""Tests for the `data-*` attributes emitted by `shiny.ui.input_date()`."""

from __future__ import annotations

from shiny import ui


def test_input_date_datesdisabled_attribute() -> None:
    html = str(
        ui.input_date("d", "Date", format="dd/mm/yyyy", datesdisabled=["2012-03-01"])
    )
    # Not `data-date-*`, which bootstrap-datepicker would parse with `format`.
    assert 'data-dates-disabled="[&quot;2012-03-01&quot;]"' in html
    assert "data-date-dates-disabled" not in html


def test_input_date_datesdisabled_omitted_when_none() -> None:
    html = str(ui.input_date("d", "Date"))
    assert "dates-disabled" not in html
