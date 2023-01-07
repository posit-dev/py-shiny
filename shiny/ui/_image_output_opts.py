import re
import sys
from typing import Dict, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class ClickOpts(TypedDict):
    id: str
    clip: bool


class BrushOpts(TypedDict):
    id: str
    fill: str
    stroke: str
    opacity: float
    delay: int
    delayType: str
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


def brush_opts(
    id: str,
    *,
    fill: str = "#9cf",
    stroke: str = "#036",
    opacity: float = 0.25,
    delay: int = 300,
    delayType: str = "debounce",
    clip: bool = True,
    direction: str = "xy",
    resetOnNew: bool = False,
) -> BrushOpts:

    return {
        "id": id,
        "fill": fill,
        "stroke": stroke,
        "opacity": opacity,
        "delay": delay,
        "delayType": delayType,
        "clip": clip,
        "direction": direction,
        "resetOnNew": resetOnNew,
    }
