from typing import TypeVar
from .types import SilentException, SilentCancelOutputException

T = TypeVar("T")


def req(*args: T, cancel_output: bool = False) -> T:
    for arg in args:
        if not arg:
            if cancel_output:
                raise SilentCancelOutputException()
            else:
                raise SilentException()
    return args[0]
