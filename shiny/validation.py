# For use with shinysession.SANITIZE_ERRORS = True
from typing import TypeVar


class SafeException(Exception):
    pass


class SilentException(Exception):
    def __init__(self, cancel_output: bool = False) -> None:
        self.cancel_output = cancel_output


T = TypeVar("T")


def req(*args: T, cancel_output: bool = False) -> T:
    for arg in args:
        if not arg:
            raise SilentException(cancel_output)
    return args[0]
