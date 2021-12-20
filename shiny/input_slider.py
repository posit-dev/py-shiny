import math
import sys
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Union, Tuple, TypeVar

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
from typing_extensions import NotRequired

from htmltools import tags, Tag, div, css, TagAttrArg, TagChildArg, HTML

from .html_dependencies import ionrangeslider_deps
from .input_utils import shiny_input_label

__all__ = ["input_slider"]

# TODO: validate value(s) are within (min,max)?

SliderValueArg = TypeVar("SliderValueArg", int, float, datetime, date)
SliderStepArg = Union[int, float, timedelta]


class AnimationOptions(TypedDict):
    interval: NotRequired[int]
    loop: NotRequired[bool]
    play_button: NotRequired[TagChildArg]
    pause_button: NotRequired[TagChildArg]


def input_slider(
    id: str,
    label: TagChildArg,
    min: SliderValueArg,
    max: SliderValueArg,
    value: Union[SliderValueArg, Tuple[SliderValueArg, SliderValueArg]],
    step: Optional[SliderStepArg] = None,
    ticks: bool = True,
    animate: Union[bool, AnimationOptions] = False,
    width: Optional[str] = None,
    sep: str = ",",
    pre: Optional[str] = None,
    post: Optional[str] = None,
    time_format: Optional[str] = None,
    timezone: Optional[str] = None,
    drag_range: bool = True,
) -> Tag:

    # Thanks to generic typing, max, value, etc. should be of the same type
    data_type = _slider_type(min)

    # Make sure min, max, value, and step are all numeric
    # (converts dates/datetimes to milliseconds since epoch...this is the value JS wants)
    min_num = _as_numeric(min)
    max_num = _as_numeric(max)
    val_nums = (
        (_as_numeric(value[0]), _as_numeric(value[1]))
        if isinstance(value, (tuple, list))
        else (_as_numeric(value), _as_numeric(value))
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

    props: Dict[str, TagAttrArg] = {
        "class_": "js-range-slider",
        "id": id,
        "style": css(width=width),
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
            class_="slider-animate-button",
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


def _as_numeric(x: Union[SliderStepArg, datetime, date]) -> Union[int, float]:
    if isinstance(x, timedelta):
        return x.total_seconds() * 1000
    if isinstance(x, datetime):
        return x.timestamp() * 1000
    if isinstance(x, date):
        return datetime(x.year, x.month, x.day).timestamp() * 1000
    return x


def _find_step_size(
    min: Union[int, float], max: Union[int, float]
) -> Union[int, float]:
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


def _play_icon() -> HTML:
    try:
        from fontawesome import icon_svg

        return icon_svg("play")
    except ImportError:
        return HTML("&#x23ef;")


def _pause_icon() -> HTML:
    try:
        from fontawesome import icon_svg

        return icon_svg("pause")
    except ImportError:
        return HTML("&#9616;&#9616;")
