from __future__ import annotations

from typing import Union, overload

__all__ = (
    "CssUnit",
    "as_css_unit",
    "as_css_padding",
)

CssUnit = Union[
    int,
    float,
    str,
]


@overload
def as_css_unit(value: None) -> None:
    ...


@overload
def as_css_unit(value: CssUnit) -> str:
    ...


def as_css_unit(value: None | CssUnit) -> None | str:
    # TODO-future: Actually validate. Or don't validate, but then change
    # the function name to to_css_unit() or something.
    if isinstance(value, (float, int)):
        # Explicit check for 0 because floats may format to have many decimals.
        if value == 0:
            return "0"
        return "{:f}px".format(value)
    else:
        return value


@overload
def as_css_padding(padding: CssUnit | list[CssUnit]) -> str:
    ...


@overload
def as_css_padding(padding: None) -> None:
    ...


def as_css_padding(padding: CssUnit | list[CssUnit] | None) -> str | None:
    if padding is None:
        return None

    if not isinstance(padding, list):
        padding = [padding]

    return " ".join(as_css_unit(p) for p in padding)


# It seems to be to use % over fr here since there is no gap on the grid
def to_width_unit(x: str | float | int) -> str:
    if isinstance(x, (int, float)):
        return as_css_unit(x)

    if isinstance(x, str) and x.endswith("%") and x.count("%") == 1:
        x1_num = float(x[:-1])
        x2_num = 100 - x1_num
        return f"{x1_num}% {x2_num}%"

    # TODO-bslib: validateCssUnit() should maybe support fr units?
    # return(paste(x, collapse = " "))
    return as_css_unit(x)
