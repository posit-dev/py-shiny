import re
import sys
from typing import Dict

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class ClickOpts(TypedDict):
    id: str
    clip: bool


def format_opt_names(opts: ClickOpts, prefix: str) -> Dict[str, str]:
    new_opts: Dict[str, str] = dict()
    for key, value in opts.items():
        new_key = f"data-{prefix}-" + re.sub("([A-Z])", "-\\1", key).lower()
        new_value = str(value)

        if isinstance(value, bool):
            new_value = new_value.lower()

        new_opts[new_key] = new_value

    return new_opts


def click_opts(id: str, clip: bool = True) -> ClickOpts:
    return {
        "id": id,
        "clip": clip,
    }
