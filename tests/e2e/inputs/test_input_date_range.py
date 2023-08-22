from __future__ import annotations

import datetime
import typing
from typing import Literal

from conftest import ShinyAppProc, create_doc_example_fixture
from controls import InputDateRange
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_date_range")


def expect_date_range(
    date: InputDateRange,
    start_value: str | Literal["today"] = "today",
    end_value: str | Literal["today"] = "today",
    *,
    label: str = "Date:",
    autoclose: bool = True,
    datesdisabled: typing.Optional[list[str]] = None,
    daysofweekdisabled: typing.Optional[list[int]] = None,
    format: str = "yyyy-mm-dd",
    language: str = "en",
    max_date: typing.Optional[str] = None,
    min_date: typing.Optional[str] = None,
    startview: str = "month",
    weekstart: int = 0,
    width: typing.Optional[str] = None,
    separator: str = " to ",
) -> None:
    start_value = str(datetime.date.today()) if start_value == "today" else start_value
    end_value = str(datetime.date.today()) if end_value == "today" else end_value
    date.expect_value((start_value, end_value))
    autoclose_str = "true" if autoclose else "false"
    date.expect_autoclose(autoclose_str)
    # # Not supported in `input_date_range()`
    # date.expect_datesdisabled(datesdisabled)
    # date.expect_daysofweekdisabled(daysofweekdisabled)
    date.expect_format(format)
    date.expect_language(language)
    date.expect_max_date(max_date)
    date.expect_min_date(min_date)
    date.expect_startview(startview)
    date.expect_weekstart(weekstart)
    date.expect_width(width)
    date.expect_separator(separator)


def test_input_date_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    daterange1 = InputDateRange(page, "daterange1")

    daterange1.expect_label("Date range:")
    expect(daterange1.loc_label).to_have_text("Date range:")

    expect_date_range(daterange1, "2001-01-01", "2010-12-31")

    daterange1.set(("2012-02-02", "2012-11-15"))
    expect_date_range(daterange1, "2012-02-02", "2012-11-15")

    expect_date_range(InputDateRange(page, "daterange2"))

    expect_date_range(
        InputDateRange(page, "daterange3"),
        "01/01/01",
        "12/31/10",
        format="mm/dd/yy",
        separator=" - ",
        min_date="2001-01-01",
        max_date="2012-12-21",
    )

    expect_date_range(
        InputDateRange(page, "daterange4"),
        str(datetime.date(2001, 1, 1)),
        str(datetime.date(2010, 12, 31)),
    )
    expect_date_range(
        InputDateRange(page, "daterange5"),
        language="de",
        weekstart=1,
    )
    expect_date_range(
        InputDateRange(page, "daterange6"),
        startview="decade",
    )
