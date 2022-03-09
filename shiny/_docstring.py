import os
from typing import Callable, Any, TypeVar, Literal

ex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")

FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


def add_example(directive: Literal["pyshinyapp"] = "pyshinyapp") -> Callable[[F], F]:
    def _(func: F) -> F:

        # To avoid a performance hit on `import shiny`, we only add examples to the
        # docstrings if this env variable is set (as it is in docs/source/conf.py).
        if os.getenv("SHINY_ADD_EXAMPLES") != "true":
            return func

        fn_name = func.__name__
        example_file = os.path.join(ex_dir, fn_name, "app.py")
        if not os.path.exists(example_file):
            raise ValueError(f"No example for {fn_name}")

        if func.__doc__ is None:
            func.__doc__ = ""

        # How many leading spaces does the docstring start with?
        doc = func.__doc__.replace("\n", "")
        indent = " " * (len(doc) - len(doc.lstrip()))

        with open(example_file) as f:
            example = indent.join([" " * 4 + x for x in f.readlines()])

        example_section = ("\n" + indent).join(
            [
                "",
                "",
                "Example",
                "-------",
                "",
                ".. code-block:: python",
                "",
                example,
                "",
                f".. {directive}::",
                "",
                example,
            ]
        )

        func.__doc__ += example_section
        return func

    return _


def doc_format(**kwargs: str) -> Callable[[F], F]:
    def _(func: F) -> F:
        if func.__doc__:
            func.__doc__ = func.__doc__.format(**kwargs)
        return func

    return _
