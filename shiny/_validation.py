from ._docstring import add_example
from .types import SilentException, SilentCancelOutputException


@add_example()
def req(*args: object, cancel_output: bool = False) -> None:
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
    """
    for arg in args:
        if not arg:
            if cancel_output:
                raise SilentCancelOutputException()
            else:
                raise SilentException()
