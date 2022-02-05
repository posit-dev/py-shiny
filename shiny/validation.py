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
        if _is_truthy(arg):
            continue
        elif cancel_output:
            raise SilentCancelOutputException()
        else:
            raise SilentException()
    return args[0]


def _is_truthy(x: object) -> bool:
    if x:
        return True
    elif x is False:
        return False
    # treat 0 as truthy since that's often meaningful (e.g., input_slider(), etc)
    elif isinstance(x, (int, float)):
        return True
    else:
        return False
