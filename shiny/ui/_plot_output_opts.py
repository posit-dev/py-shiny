import re
import sys
from typing import Dict, Union

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict


class ClickOpts(TypedDict):
    id: str
    clip: bool


class DblClickOpts(TypedDict):
    id: str
    clip: bool
    delay: int


class HoverOpts(TypedDict):
    id: str
    delay: int
    delayType: Literal["debounce", "throttle"]
    clip: bool
    nullOutside: bool


class BrushOpts(TypedDict):
    id: str
    fill: str
    stroke: str
    opacity: float
    delay: int
    delayType: Literal["debounce", "throttle"]
    clip: bool
    direction: str
    resetOnNew: bool


# It would be better if opts could just be a Dict[str, Union[str, bool]], but ClickOpts
# is a TypedDict, and that is _not_ a subclass of Dict because it doesn't support some
# Dict operations, like removing items specified in the TypedDict.
def format_opt_names(
    opts: Union[Dict[str, Union[str, bool]], ClickOpts],
    prefix: str,
) -> Dict[str, str]:
    new_opts: Dict[str, str] = dict()
    for key, value in opts.items():
        new_key = f"data-{prefix}-" + re.sub("([A-Z])", "-\\1", key).lower()
        new_value = str(value)

        if isinstance(value, bool):
            new_value = new_value.lower()

        new_opts[new_key] = new_value

    return new_opts


def click_opts(
    id: str,
    *,
    clip: bool = True,
) -> ClickOpts:
    return {
        "id": id,
        "clip": clip,
    }


def dblclick_opts(
    id: str,
    *,
    delay: int = 400,
    clip: bool = True,
) -> DblClickOpts:
    return {
        "id": id,
        "delay": delay,
        "clip": clip,
    }


def hover_opts(
    id: str,
    *,
    delay: int = 300,
    delay_type: Literal["debounce", "throttle"] = "debounce",
    clip: bool = True,
    null_outside: bool = True,
) -> HoverOpts:
    return {
        "id": id,
        "delay": delay,
        "delayType": delay_type,
        "clip": clip,
        "nullOutside": null_outside,
    }


def brush_opts(
    id: str,
    *,
    fill: str = "#9cf",
    stroke: str = "#036",
    opacity: float = 0.25,
    delay: int = 300,
    delay_type: Literal["debounce", "throttle"] = "debounce",
    clip: bool = True,
    direction: str = "xy",
    reset_on_new: bool = False,
) -> BrushOpts:
    return {
        "id": id,
        "fill": fill,
        "stroke": stroke,
        "opacity": opacity,
        "delay": delay,
        "delayType": delay_type,
        "clip": clip,
        "direction": direction,
        "resetOnNew": reset_on_new,
    }
