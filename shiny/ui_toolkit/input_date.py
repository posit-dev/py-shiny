import json
from datetime import date
from typing import Optional

from htmltools import tags, Tag, div, span, TagAttrArg, TagChildArg, css

from .html_dependencies import datepicker_deps
from .input_utils import shiny_input_label

__all__ = ["input_date", "input_date_range"]


def input_date(
    id: str,
    label: TagChildArg,
    value: Optional[date] = None,
    min: Optional[date] = None,
    max: Optional[date] = None,
    format: str = "yyyy-mm-dd",
    startview: str = "month",
    weekstart: int = 0,
    language: str = "en",
    width: Optional[str] = None,
    autoclose: bool = True,
    datesdisabled: Optional[str] = None,
    daysofweekdisabled: Optional[str] = None,
) -> Tag:
    # TODO: needed?
    # value = dateYMD(value, "value")
    # min = dateYMD(min, "min")
    # max = dateYMD(max, "max")
    # datesdisabled = dateYMD(datesdisabled, "datesdisabled")
    return div(
        shiny_input_label(id, label),
        date_input_tag(
            id=id,
            value=value,
            min=min,
            max=max,
            format=format,
            startview=startview,
            weekstart=weekstart,
            language=language,
            autoclose=autoclose,
            data_date_dates_disabled=json.dumps(datesdisabled),
            data_date_days_of_week_disabled=json.dumps(daysofweekdisabled),
        ),
        id=id,
        class_="shiny-date-input form-group shiny-input-container",
        style=css(width=width),
    )


def input_date_range(
    id: str,
    label: TagChildArg,
    start: Optional[date] = None,
    end: Optional[date] = None,
    min: Optional[date] = None,
    max: Optional[date] = None,
    format: str = "yyyy-mm-dd",
    startview: str = "month",
    weekstart: int = 0,
    language: str = "en",
    separator: str = " to ",
    width: Optional[str] = None,
    autoclose: bool = True,
) -> Tag:
    # TODO: needed?
    # start = dateYMD(start, "start")
    # end = dateYMD(end, "end")
    # min = dateYMD(min, "min")
    # max = dateYMD(max, "max")
    return div(
        shiny_input_label(id, label),
        div(
            date_input_tag(
                id=id,
                value=start,
                min=min,
                max=max,
                format=format,
                startview=startview,
                weekstart=weekstart,
                language=language,
                autoclose=autoclose,
            ),
            # input-group-prepend and input-group-append are for bootstrap 4 forward compat
            span(
                span(separator, class_="input-group-text"),
                class_="input-group-addon input-group-prepend input-group-append",
            ),
            date_input_tag(
                id=id,
                value=end,
                min=min,
                max=max,
                format=format,
                startview=startview,
                weekstart=weekstart,
                language=language,
                autoclose=autoclose,
            ),
            # input-daterange class is needed for dropdown behavior
            class_="input-daterange input-group input-group-sm",
        ),
        id=id,
        class_="shiny-date-range-input form-group shiny-input-container",
        style=css(width=width),
    )


def date_input_tag(
    id: str,
    value: Optional[date],
    min: Optional[date],
    max: Optional[date],
    format: str,
    startview: str,
    weekstart: int,
    language: str,
    autoclose: bool,
    **kwargs: TagAttrArg,
):
    return tags.input(
        datepicker_deps(),
        {"class": "form-control"},
        type="text",
        # `aria-labelledby` attribute is required for accessibility to avoid doubled labels (#2951).
        aria_labelledby=id + "-label",
        # title attribute is announced for screen readers for date format.
        title="Date format: " + format,
        data_date_language=language,
        data_date_week_start=weekstart,
        data_date_format=format,
        data_date_start_view=startview,
        data_min_date=min,
        data_max_date=max,
        data_initial_date=value,
        data_date_autoclose="true" if autoclose else "false",
        **kwargs,
    )
