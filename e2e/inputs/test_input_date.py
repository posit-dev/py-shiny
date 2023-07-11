from __future__ import annotations

import datetime
import typing
from typing import Literal

from conftest import ShinyAppProc, create_doc_example_fixture
from controls import InputDate
from playwright.sync_api import Page, expect

app = create_doc_example_fixture("input_date")


def expect_date(
    date: InputDate,
    value: str | Literal["today"] = "today",
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
) -> None:
    date.expect_value(str(datetime.date.today()) if value == "today" else value)
    autoclose_str = "true" if autoclose else "false"
    date.expect_autoclose(autoclose_str)
    date.expect_datesdisabled(datesdisabled)
    date.expect_daysofweekdisabled(daysofweekdisabled)
    date.expect_format(format)
    date.expect_language(language)
    date.expect_max_date(max_date)
    date.expect_min_date(min_date)
    date.expect_startview(startview)
    date.expect_weekstart(weekstart)
    date.expect_width(width)


def test_input_date_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    date1 = InputDate(page, "date1")

    date1.expect_label("Date:")
    expect(date1.loc_label).to_have_text("Date:")

    expect_date(date1, "2016-02-29")

    date1.set("2016-02-15")
    expect_date(date1, "2016-02-15")

    expect_date(InputDate(page, "date2"))

    expect_date(InputDate(page, "date3"), "02/29/16", format="mm/dd/yy")

    expect_date(InputDate(page, "date3"), "02/29/16", format="mm/dd/yy")

    expect_date(InputDate(page, "date4"), "2016-02-29")

    expect_date(InputDate(page, "date5"), language="ru", weekstart=1)

    expect_date(InputDate(page, "date6"), startview="decade")

    expect_date(InputDate(page, "date7"), daysofweekdisabled=[1, 2])

    expect_date(
        InputDate(page, "date8"),
        "2016-02-29",
        datesdisabled=["2016-03-01", "2016-03-02"],
    )
