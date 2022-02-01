import json
from datetime import date
from typing import Optional, List, Union

from htmltools import tags, Tag, div, span, TagAttrArg, TagChildArg, css

from .html_dependencies import datepicker_deps
from .input_utils import shiny_input_label

__all__ = ["input_date", "input_date_range"]


def input_date(
    id: str,
    label: TagChildArg,
    value: Optional[Union[date, str]] = None,
    min: Optional[Union[date, str]] = None,
    max: Optional[Union[date, str]] = None,
    format: str = "yyyy-mm-dd",
    startview: str = "month",
    weekstart: int = 0,
    language: str = "en",
    width: Optional[str] = None,
    autoclose: bool = True,
    datesdisabled: Optional[List[str]] = None,
    daysofweekdisabled: Optional[List[int]] = None,
) -> Tag:
    return div(
        shiny_input_label(id, label),
        _date_input_tag(
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
    start: Optional[Union[date, str]] = None,
    end: Optional[Union[date, str]] = None,
    min: Optional[Union[date, str]] = None,
    max: Optional[Union[date, str]] = None,
    format: str = "yyyy-mm-dd",
    startview: str = "month",
    weekstart: int = 0,
    language: str = "en",
    separator: str = " to ",
    width: Optional[str] = None,
    autoclose: bool = True,
) -> Tag:
    return div(
        shiny_input_label(id, label),
        div(
            _date_input_tag(
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
            _date_input_tag(
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


def _date_input_tag(
    id: str,
    value: Optional[Union[date, str]],
    min: Optional[Union[date, str]],
    max: Optional[Union[date, str]],
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
        data_min_date=_as_date_attr(min),
        data_max_date=_as_date_attr(max),
        data_initial_date=_as_date_attr(value),
        data_date_autoclose="true" if autoclose else "false",
        **kwargs,
    )


def _as_date_attr(x: Optional[Union[date, str]]) -> Optional[str]:
    if x is None:
        return None
    if isinstance(x, date):
        return str(x)
    return str(date.fromisoformat(x))
