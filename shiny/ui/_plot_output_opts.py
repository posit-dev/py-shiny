from __future__ import annotations

import re
from typing import Literal

from .._typing_extensions import NotRequired, TypedDict


class ClickOpts(TypedDict):
    id: NotRequired[str]
    clip: bool


class DblClickOpts(TypedDict):
    id: NotRequired[str]
    clip: bool
    delay: int


class HoverOpts(TypedDict):
    id: NotRequired[str]
    delay: int
    delayType: Literal["debounce", "throttle"]
    clip: bool
    nullOutside: bool


class BrushOpts(TypedDict):
    id: NotRequired[str]
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
    opts: ClickOpts | DblClickOpts | HoverOpts | BrushOpts,
    prefix: str,
) -> dict[str, str]:
    new_opts: dict[str, str] = dict()
    for key, value in opts.items():
        new_key = f"data-{prefix}-" + re.sub("([A-Z])", "-\\1", key).lower()
        new_value = str(value)

        if isinstance(value, bool):
            new_value = new_value.lower()

        new_opts[new_key] = new_value

    return new_opts


def click_opts(
    *,
    clip: bool = True,
) -> ClickOpts:
    return {
        "clip": clip,
    }


def dblclick_opts(
    *,
    delay: int = 400,
    clip: bool = True,
) -> DblClickOpts:
    return {
        "delay": delay,
        "clip": clip,
    }


def hover_opts(
    *,
    delay: int = 300,
    delay_type: Literal["debounce", "throttle"] = "debounce",
    clip: bool = True,
    null_outside: bool = True,
) -> HoverOpts:
    return {
        "delay": delay,
        "delayType": delay_type,
        "clip": clip,
        "nullOutside": null_outside,
    }


def brush_opts(
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
        "fill": fill,
        "stroke": stroke,
        "opacity": opacity,
        "delay": delay,
        "delayType": delay_type,
        "clip": clip,
        "direction": direction,
        "resetOnNew": reset_on_new,
    }
