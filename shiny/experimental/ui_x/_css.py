from __future__ import annotations

import numbers
from typing import Optional, Union

CssUnitX = Union[numbers.Number, int, float, str]


def trinary(x: Optional[bool | str]) -> None | str:
    if x is None:
        return None
    if x:
        return "true"
    else:
        return "false"


def classes(*args: Optional[str]) -> Optional[str]:
    return " ".join([x for x in args if x is not None])


def validate_css_unit_x(value: None | CssUnitX) -> None | str:
    # TODO: Actually validate. Or don't validate, but then change
    # the function name to to_css_unit() or something.
    # TODO: pylance can't figure out if an `int` or `float` is a `numbers.Number` (which
    # is it). For now, use the extra types
    if (
        isinstance(value, numbers.Number)
        or isinstance(value, float)
        or isinstance(value, int)
    ):
        return "{:f}px".format(value)
    else:
        return value
