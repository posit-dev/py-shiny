from __future__ import annotations
from typing import TypeVar, cast

from ._docstring import add_example
from .types import SilentCancelOutputException, SilentException

T = TypeVar("T")


@add_example()
def req(*args: T, cancel_output: bool = False) -> T:
    """
    Throw a silent exception for falsey values.

    This is a convenient shorthand for throwing :func:`~shiny.types.SilentException` /
    :func:`~shiny.types.SilentCancelOutputException` if any of the arguments are falsey.

    Parameters
    ----------
    args
        Any number of arguments to check.
    cancel_output
        If ``True``, throw :func:`~shiny.types.SilentCancelOutputException` instead of
        :func:`~shiny.types.SilentException`.

    Returns
    -------
        The first argument.
    """
    for arg in args:
        if not arg:
            if cancel_output:
                raise SilentCancelOutputException()
            else:
                raise SilentException()

    return cast(T, None) if len(args) == 0 else args[0]
