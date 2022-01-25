# For use with ShinyApp().SANITIZE_ERRORS = True
from typing import TypeVar


class SafeException(Exception):
    pass


class SilentException(Exception):
    pass


class SilentCancelOutputException(Exception):
    pass


T = TypeVar("T")


def req(*args: T, cancel_output: bool = False) -> T:
    for arg in args:
        if not arg:
            if cancel_output:
                raise SilentCancelOutputException()
            else:
                raise SilentException()
    return args[0]
