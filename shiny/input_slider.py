from htmltools import tags, tag, div, css, TagAttr
from typing import Dict, Optional, Union, Tuple
from datetime import date, datetime
import math
import numpy
from .html_dependencies import ionrangeslider_deps
from .input_utils import *

__all__ = ["input_slider"]

SliderVal = Union[float, date, datetime]
SliderTuple = Union[Tuple[float, float], Tuple[date, date], Tuple[datetime, datetime]]
SliderVals = Union[SliderVal, SliderTuple]


def input_slider(
    id: str,
    label: str,
    min: SliderVal,
    max: SliderVal,
    value: SliderVals,
    step: Optional[SliderVal] = None,
    round: bool = False,
    ticks: bool = True,
    animate: bool = False,
    width: Optional[str] = None,
    sep: str = ",",
    pre: Optional[str] = None,
    post: Optional[str] = None,
    time_format: Optional[str] = None,
    timezone: Optional[str] = None,
    drag_range: bool = True,
) -> tag:

    vals: Tuple[SliderVal, SliderVal] = (
        value
        if isinstance(value, tuple)
        else (
            value,
            value,
        )
    )

    # TODO: validate min/max/value?
    data_type = get_slider_type(min, max, vals)

    if not step:
        step = find_step_size(min, max)

    # Convert values to milliseconds since epoch (this is the value JS uses)
    if data_type == "date":
        # TODO: Find step size in ms
        # step  = to_ms(max) - to_ms(max - step)
        min = min.timestamp() * 1000
        max = max.timestamp() * 1000
        value = value.timestamp() * 1000

    n_ticks = None
    # TODO: Try to get a sane number of tick marks
    if ticks:
        n_steps = (max - min) / step
        # Make sure there are <= 10 steps.
        # n_ticks can be a noninteger, which is good when the range is not an
        # integer multiple of the step size, e.g., min=1, max=10, step=4
        scale_factor = math.ceil(n_steps / 10)
        n_ticks = n_steps / scale_factor

    props: Dict[str, TagAttr] = {
        "class_": "js-range-slider",
        "id": id,
        "style": css(width=width),
        "data_skin": "shiny",
        # TODO: do we need to worry about scientific notation (i.e., formatNoSci()?)
        "data_min": str(min),
        "data_max": str(max),
        "data_from": str(vals[0]),
        "data_step": str(step),
        "data_grid": str(ticks),
        "data_grid_num": n_ticks,
        "data_grid_snap": "false",
        # "data_prettify_separator": sep,
        # "data_prettify_enabled": sep != "",
        "data_prefix": pre,
        "data_postfix": post,
        "data_keyboard": "true",
        "data_data_type": data_type,
        "data_time_format": time_format,
        "data_timezone": timezone,
    }

    if isinstance(value, tuple):
        props["data_type"] = "double"
        props["data_to"] = value[1]
        props["data_drag_interval"] = drag_range

    if not time_format and data_type[0:4] == "date":
        props["data_time_format"] = "%F" if data_type == "date" else "%F %T"

    # 1. ionRangeSlider wants attr = 'true'/'false'
    props = {k: str(v).lower() if isinstance(v, bool) else v for k, v in props.items()}

    return div(
        shiny_input_label(id, label),
        tags.input(**props),
        *ionrangeslider_deps(),
        class_="form-group shiny-input-container",
    )


def get_slider_type(min: SliderVal, max: SliderVal, value: SliderVals) -> str:
    vals = (min, max) + value
    type = set(map(slider_type, vals))
    if len(type) == 1:
        return type.pop()
    else:
        raise Exception(
            f"slider()'s `min`, `max`, and `value` arguments must be all the same type, but were given multiple: {type}"
        )


def slider_type(x: SliderVal) -> str:
    if isinstance(x, date):
        return "date"
    if isinstance(x, datetime):
        return "datetime"
    return "number"


def find_step_size(min: SliderVal, max: SliderVal) -> Union[int, float]:
    # TODO: this is a naive version of shiny::findStepSize() that might be susceptible to
    # rounding errors? https://github.com/rstudio/shiny/pull/1956
    range = max - min
    if range < 2 or isinstance(min, float) or isinstance(max, float):
        steps = numpy.linspace(min, max, 100)
        return steps[1] - steps[0]
    else:
        return 1
