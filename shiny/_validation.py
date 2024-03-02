from __future__ import annotations

from typing import Literal, TypeVar, overload

from ._docstring import add_example
from .types import (
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)

T = TypeVar("T")


@overload
def req(*, cancel_output: bool | Literal["progress"] = False) -> None: ...


@overload
def req(*args: T, cancel_output: bool | Literal["progress"] = False) -> T: ...


@add_example()
def req(*args: T, cancel_output: bool | Literal["progress"] = False) -> T | None:
    """
    Throw a silent exception for falsy values.

    This is a convenient shorthand for throwing :class:`~shiny.types.SilentException` /
    :class:`~shiny.types.SilentCancelOutputException` if any of the arguments are falsy.

    The term "falsy" generally indicates that a value is considered `False` when
    encountered in a logical context. We use the term a little loosely here; our usage
    tries to match the intuitive notions of "Is this value missing or available?", or
    "Has the user provided an answer?", or in the case of action buttons, "Has the
    button been clicked?". So `False`, `None`, `0`, and `""` would be examples of Falsy
    values.

    Parameters
    ----------
    *args
        Any number of arguments to check.
    cancel_output
        If ``True``, throw :class:`~shiny.types.SilentCancelOutputException` instead of
        :class:`~shiny.types.SilentException`.

    Returns
    -------
    :
        The first argument. If no arguments are provided, returns ``None``.
    """
    if len(args) == 0:
        return None

    for arg in args:
        if not arg:
            if cancel_output is True:
                raise SilentCancelOutputException()
            elif cancel_output == "progress":
                raise SilentOperationInProgressException()
            else:
                raise SilentException()

    return args[0]
