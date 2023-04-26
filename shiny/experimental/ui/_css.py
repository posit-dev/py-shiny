from __future__ import annotations

import numbers
from typing import Union, overload

CssUnit = Union[
    # TODO: pylance really doesn't like `numbers.Number`.
    #       Instead, use `int` and `float`
    int,
    float,
    str,
]


@overload
def trinary(x: None) -> None:
    ...


@overload
def trinary(x: bool | str) -> str:
    ...


def trinary(x: bool | str | None) -> None | str:
    if x is None:
        return None
    elif x:
        return "true"
    else:
        return "false"


@overload
def validate_css_unit(value: None) -> None:
    ...


@overload
def validate_css_unit(value: CssUnit) -> str:
    ...


def validate_css_unit(value: None | CssUnit) -> None | str:
    # TODO-future: Actually validate. Or don't validate, but then change
    # the function name to to_css_unit() or something.
    # TODO-future: pylance can't figure out if an `int` or `float` is a `numbers.Number` (which
    # is it). For now, use the extra types
    if (
        isinstance(value, numbers.Number)
        or isinstance(value, float)
        or isinstance(value, int)
    ):
        # Explicit check for 0 because floats may format to have many decimals.
        if value == 0:
            return "0"
        return "{:f}px".format(value)
    else:
        return value
