from .types import SilentException, SilentCancelOutputException


def req(*args: object, cancel_output: bool = False) -> None:
    for arg in args:
        if not arg:
            if cancel_output:
                raise SilentCancelOutputException()
            else:
                raise SilentException()
