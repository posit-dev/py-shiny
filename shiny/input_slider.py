from typing import Optional, Union, Tuple, List
from htmltools import tags, tag, html_dependency
from datetime import date, datetime
from .utils import shiny_input_label
import math
import numpy

SliderVal = Union[float, date, datetime]
SliderVals = Union[SliderVal, Tuple[SliderVal, SliderVal]]

def input_slider(id: str, label: str, min: SliderVal, max: SliderVal, value: SliderVals,
         step: Optional[SliderVal] = None, round: bool = False, ticks: bool = True,
         animate: bool = False, width: Optional[str] = None,
         sep = ",", pre = None, post = None, time_format: Optional[str] = None,
         timezone: Optional[str] = None, drag_range: bool = True) -> tag:

  value = value if isinstance(value, tuple) else (value, )

  # TODO: validate min/max/value?
  data_type = get_slider_type(min, max, value)

  if not step:
    step = find_step_size(min, max)

  # Convert values to milliseconds since epoch (this is the value JS uses)
  if data_type == "date":
    # TODO: Find step size in ms
    #step  = to_ms(max) - to_ms(max - step)
    min   = min.timestamp() * 1000
    max   = max.timestamp() * 1000
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

  props = {
    "className": "js-range-slider",
    "id": id,
    "data_skin": "shiny",
    "data_min": min, # TODO: do we need to worry about scientific notation (i.e., formatNoSci()?)
    "data_max": max,
    "data_from": value[0],
    "data_step": step,
    "data_grid": ticks,
    "data_grid_num": n_ticks,
    "data_grid_snap": False,
    "data_prettify_separator": sep,
    "data_prettify_enabled": sep != "",
    "data_prefix": pre,
    "data_postfix": post,
    "data_keyboard": True,
    "data_data_type": data_type,
    "data_time_format": time_format,
    "data_timezone": timezone
  }

  if len(value) == 2:
    props["data_type"] = "double"
    props["data_to"] = value[1]
    props["data_drag_interval"] = drag_range

  if not time_format and data_type[0:4] == "date":
    props["data_time_format"] = "%F" if data_type == "date" else "%F %T"

  if width: props["style"] = "width:{width};"
  # 1. ionRangeSlider wants attr = 'true'/'false'
  # 2. drop attr='None' (dominate should really do this automatically)
  props = {
    k: str(v).lower() if isinstance(v, bool) else v for k, v in props.items() if v is not None
  }

  container = tags.div(
    shiny_input_label(id, label),
    tags.input(**props),
    ionrangeslider_libs(),
    _class_ = "form-group shiny-input-container"
  )

  return container


def get_slider_type(min: SliderVal, max: SliderVal, value: SliderVals) -> str:
  vals = (min, max) + value
  type = set(map(slider_type, vals))
  if len(type) == 1 :
    return type.pop()
  else :
    raise Exception(f"slider()'s `min`, `max`, and `value` arguments must be all the same type, but were given multiple: {type}")

def slider_type(x: SliderVal) -> str:
  if isinstance(x, date):
      return "date"
  if isinstance(x, datetime):
      return "datetime"
  return "number"


def find_step_size(min: SliderVal, max: SliderVal):
  # TODO: this is a naive version of shiny::findStepSize() that might be susceptible to
  # rounding errors? https://github.com/rstudio/shiny/pull/1956
  range = max - min
  if range < 2 or isinstance(min, float) or isinstance(max, float):
    steps = numpy.linspace(min, max, 100)
    return steps[1] - steps[0]
  else:
    return 1

def ionrangeslider_libs() -> List[html_dependency]:
  return [
    html_dependency(
      name = "ionrangeslider",
      version = "2.3.1",
      package = "shiny",
      src = "www/shared/ionrangeslider",
      script = "js/ion.rangeSlider.min.js",
      stylesheet = "css/ion.rangeSlider.css",
    ),
    html_dependency(
      name = "strftime",
      version = "0.9.2",
      package = "shiny",
      src = "www/shared/strftime",
      script = "strftime-min.js"
    )
  ]