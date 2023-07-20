from __future__ import annotations

__all__ = (
    "input_slider",
    "SliderValueArg",
    "SliderStepArg",
    "AnimationOptions",
)

import math
from datetime import date, datetime, timedelta
from typing import Iterable, Optional, TypeVar, Union, cast

from htmltools import HTML, Tag, TagAttrValue, TagChild, css, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from .._typing_extensions import NotRequired, TypedDict
from ._html_dependencies import ionrangeslider_deps
from ._utils import shiny_input_label

# TODO: validate value(s) are within (min,max)?

SliderValueArg = TypeVar("SliderValueArg", float, datetime, date)
SliderStepArg = Union[float, timedelta]


class AnimationOptions(TypedDict):
    """
    Options for the animation of a :func:`input_slider`.

    Parameters
    ----------
    interval
        The interval, in milliseconds, between each animation step.
    loop
        ``True`` to automatically restart the animation when it reaches the end.
    play_button
        Play button text or HTML.
    pause_button
        Pause button text or HTML.

    Returns
    -------
    :
        A TypedDict.

    See Also
    --------
    ~shiny.ui.input_slider
    """

    interval: NotRequired[int]
    loop: NotRequired[bool]
    play_button: NotRequired[TagChild]
    pause_button: NotRequired[TagChild]


@add_example()
def input_slider(
    id: str,
    label: TagChild,
    min: SliderValueArg,
    max: SliderValueArg,
    value: SliderValueArg | Iterable[SliderValueArg],
    *,
    step: Optional[SliderStepArg] = None,
    ticks: bool = False,
    animate: bool | AnimationOptions = False,
    width: Optional[str] = None,
    sep: str = ",",
    pre: Optional[str] = None,
    post: Optional[str] = None,
    time_format: Optional[str] = None,
    timezone: Optional[str] = None,
    drag_range: bool = True,
) -> Tag:
    """
    Constructs a slider widget to select a number, date, or date-time from a range.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    value
        Initial value.
    step
        Interval to use when stepping between min and max.
    ticks
        ``False`` to hide tick marks, ``True`` to show them according to some simple
        heuristics.
    animate
        ``True`` to show simple animation controls with default settings; ``False`` not
        to; or a custom settings list, such as those created using
        :class:`AnimationOptions()`.
    width
        The CSS width, e.g. '400px', or '100%'
    sep
        Separator between thousands places in numbers.
    pre
        A prefix string to put in front of the value.
    post
        A suffix string to put after the value.
    time_format
        Only used if the slider values are :class:`~datetime.date` or
        :class:`~datetime.datetime` objects. A time format string, to be passed to the
        Javascript strftime library. See https://github.com/samsonjs/strftime for more
        details. For Dates, the default is "%F" (like "2015-07-01"), and for Datetimes,
        the default is "%F %T" (like "2015-07-01 15:32:10").
    timezone
        Only used if the values are :class:`~datetime.datetime` objects. A string
        specifying the time zone offset for the displayed times, in the format "+HHMM"
        or "-HHMM". If ``None`` (the default), times will be displayed in the browser's
        time zone. The value "+0000" will result in UTC time.
    drag_range
        This option is used only if it is a range slider (with two values). If ``True``
        (the default), the range can be dragged. In other words, the min and max can be
        dragged together. If ``False``, the range cannot be dragged.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A number, date, or date-time (depending on the class of value), or in the case of
    slider range, a list of two numbers/dates/date-times.
    :::

    See Also
    -------
    ~shiny.ui.update_slider
    """

    # Thanks to generic typing, max, value, etc. should be of the same type
    data_type = _slider_type(min)

    # Make sure min, max, value, and step are all numeric
    # (converts dates/datetimes to milliseconds since epoch...this is the value JS wants)
    min_num = _as_numeric(min)
    max_num = _as_numeric(max)
    val_nums = (
        (_as_numeric(value[0]), _as_numeric(value[1]))
        if isinstance(value, (tuple, list))
        else (
            _as_numeric(cast(SliderValueArg, value)),
            _as_numeric(cast(SliderValueArg, value)),
        )
    )
    step_num = _find_step_size(min_num, max_num) if step is None else _as_numeric(step)

    n_ticks = None
    if ticks:
        n_steps = (max_num - min_num) / step_num
        # Make sure there are <= 10 steps.
        # n_ticks can be a noninteger, which is good when the range is not an
        # integer multiple of the step size, e.g., min=1, max=10, step=4
        scale_factor = math.ceil(n_steps / 10)
        n_ticks = n_steps / scale_factor

    id = resolve_id(id)

    props: dict[str, TagAttrValue] = {
        "class": "js-range-slider",
        "id": id,
        "data_skin": "shiny",
        # TODO: do we need to worry about scientific notation (i.e., formatNoSci()?)
        "data_min": str(min_num),
        "data_max": str(max_num),
        "data_from": str(val_nums[0]),
        "data_step": str(step_num),
        "data_grid": ticks,
        "data_grid_num": n_ticks,
        "data_grid_snap": "false",
        "data_prettify_separator": sep,
        "data_prettify_enabled": sep != "",
        "data_prefix": pre,
        "data_postfix": post,
        "data_keyboard": "true",
        "data_data_type": data_type,
        "data_time_format": time_format,
        "data_timezone": timezone,
    }

    if isinstance(value, (tuple, list)):
        props["data_type"] = "double"
        props["data_to"] = str(val_nums[1])
        props["data_drag_interval"] = drag_range

    if not time_format and data_type[0:4] == "date":
        props["data_time_format"] = "%F" if data_type == "date" else "%F %T"

    # ionRangeSlider wants attr = 'true'/'false'
    props = {k: str(v).lower() if isinstance(v, bool) else v for k, v in props.items()}

    slider_tag = div(
        shiny_input_label(id, label),
        tags.input(**props),
        *ionrangeslider_deps(),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )

    if animate is False:
        return slider_tag

    if animate is True:
        animate = AnimationOptions()

    animate_tag = div(
        tags.a(
            tags.span(animate.get("play_button", _play_icon()), class_="play"),
            tags.span(animate.get("pause_button", _pause_icon()), class_="pause"),
            href="#",
            class_="slider-animate-button link-secondary",
            data_target_id=id,
            data_interval=animate.get("interval", 500),
            data_loop=animate.get("loop", True),
        ),
        class_="slider-animate-container",
    )

    slider_tag.append(animate_tag)

    return slider_tag


def _slider_type(x: SliderValueArg) -> str:
    if isinstance(x, datetime):
        return "datetime"
    if isinstance(x, date):
        return "date"
    return "number"


def _as_numeric(x: SliderStepArg | datetime | date) -> float:
    if isinstance(x, timedelta):
        return x.total_seconds() * 1000
    if isinstance(x, datetime):
        return x.timestamp() * 1000
    if isinstance(x, date):
        return datetime(x.year, x.month, x.day).timestamp() * 1000
    return x


def _find_step_size(min: int | float, max: int | float) -> int | float:
    # TODO: this is a naive version of shiny::findStepSize() that might be susceptible to
    # rounding errors? https://github.com/rstudio/shiny/pull/1956
    range = max - min

    if range < 2 or isinstance(min, float) or isinstance(max, float):
        step = range / 100
        # Round the step to get rid of any floating point arithmetic errors by
        # mimicing what signif(digits = 10, step) does in R (see Description of ?signif)
        # (the basic intuition is that smaller differences need more precision)
        return round(step, 10 - math.ceil(math.log10(step)))
    else:
        return 1


play_icon = """<svg viewBox="0 0 448 512" preserveAspectRatio="none" aria-hidden="true" role="img" style="fill:currentColor;height:1em;width:0.88em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;font-size:inherit;overflow:visible;">
  <title>Play</title>
  <!-- Font Awesome Free 5.15.4 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) -->
  <path d="M424.4 214.7L72.4 6.6C43.8-10.3 0 6.1 0 47.9V464c0 37.5 40.7 60.1 72.4 41.3l352-208c31.4-18.5 31.5-64.1 0-82.6z"></path>
</svg>"""

pause_icon = """<svg viewBox="0 0 448 512" preserveAspectRatio="none" aria-hidden="true" role="img" style="fill:currentColor;height:1em;width:0.88em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;font-size:inherit;overflow:visible;">
  <title>Pause</title>
  <!-- Font Awesome Free 5.15.4 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) -->
  <path d="M144 479H48c-26.5 0-48-21.5-48-48V79c0-26.5 21.5-48 48-48h96c26.5 0 48 21.5 48 48v352c0 26.5-21.5 48-48 48zm304-48V79c0-26.5-21.5-48-48-48h-96c-26.5 0-48 21.5-48 48v352c0 26.5 21.5 48 48 48h96c26.5 0 48-21.5 48-48z"></path>
</svg>"""


def _play_icon() -> Tag | HTML:
    return HTML(play_icon)


def _pause_icon() -> Tag | HTML:
    return HTML(pause_icon)
