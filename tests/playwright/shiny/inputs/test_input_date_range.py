from __future__ import annotations

import datetime
import typing
from typing import Literal

from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("input_date_range")


def expect_date_range(
    date: controller.InputDateRange,
    start_value: str | Literal["today"] = "today",
    end_value: str | Literal["today"] = "today",
    *,
    autoclose: bool = True,
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

    daterange1 = controller.InputDateRange(page, "daterange1")

    daterange1.expect_label("Date range:")
    today = str(datetime.date.today().strftime("%Y-%m-%d"))
    tommorow = str(
        (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    )
    daterange1.set((today, today))
    expect_date_range(daterange1, today, today)
    daterange1.set((today, tommorow))

    expect_date_range(
        controller.InputDateRange(page, "daterange2"), "2001-01-01", "2010-12-31"
    )

    expect_date_range(
        controller.InputDateRange(page, "daterange3"),
        "01/01/01",
        "12/31/10",
        format="mm/dd/yy",
        separator=" - ",
        min_date="2001-01-01",
        max_date="2012-12-21",
    )

    expect_date_range(
        controller.InputDateRange(page, "daterange4"),
        str(datetime.date(2001, 1, 1)),
        str(datetime.date(2010, 12, 31)),
    )
    expect_date_range(
        controller.InputDateRange(page, "daterange5"),
        language="de",
        weekstart=1,
    )
    expect_date_range(
        controller.InputDateRange(page, "daterange6"),
        startview="decade",
    )

    expect_date_range(
        controller.InputDateRange(page, "daterange7"),
        width="600px",
    )

    expect_date_range(
        controller.InputDateRange(page, "daterange8"),
        autoclose=False,
    )
