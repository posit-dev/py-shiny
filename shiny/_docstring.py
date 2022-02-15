import os
from typing import Callable, Any, TypeVar

ex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")

FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


def add_example() -> Callable[[F], F]:
    def _(func: F) -> F:
        fn_name = func.__name__
        example_file = os.path.join(ex_dir, fn_name, "app.py")
        if not os.path.exists(example_file):
            raise ValueError(f"No example for {fn_name}")

        with open(example_file) as f:
            example = [" " * 8 + x for x in f.readlines()]
            example = "".join(example)

        if func.__doc__ is None:
            func.__doc__ = ""

        func.__doc__ += (
            f"\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n{example}"
        )

        return func

    return _


def doc_format(**kwargs: str) -> Callable[[F], F]:
    def _(func: F) -> F:
        if func.__doc__:
            func.__doc__ = func.__doc__.format(**kwargs)
        return func

    return _
