import os
import sys
from typing import Callable, TypeVar, List

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

ex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")

P = ParamSpec("P")
T = TypeVar("T")


def add_example(
    directive: Literal[
        "shinyapp::", "shinyeditor::", "code-block:: python", "cell::", "terminal::"
    ] = "shinyeditor::",
    **options: str,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Add an example to the docstring of a function, method, or class.

    This decorator must, at the moment, be used on a function, method, or class whose
    ``__name__`` matches the name of directory under ``shiny/examples/``, and must
    also contain a ``app.py`` file in that directory.

    Parameters
    ----------
    directive
        A directive for rendering the example. This can be one of:
            - ``shinyapp``: A live shiny app (statically served via wasm).
            - ``code``: A python code snippet.
            - ``shinyeditor``: A live shiny app (statically served via wasm).
            - ``cell``: A executable Python cell.
            - ``terminal``: A minimal Python IDE
    **options
        Options for the directive. See docs/source/sphinxext/pyshinyapp.py for details.
    """

    def _(func: Callable[P, T]) -> Callable[P, T]:

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

        # When rendering a standalone app, put the code above it (maybe this should be
        # handled by the directive itself?)
        example_prefix: List[str] = []
        if directive == "shinyapp::":
            example_prefix.extend(
                [
                    ".. code-block:: python",
                    "",
                    example,
                    "",
                ]
            )

        example_section = ("\n" + indent).join(
            [
                "",
                "",
                "Example",
                "-------",
                "",
                *example_prefix,
                f".. {directive}",
                *[f"{indent}:{k}: {v}" for k, v in options.items()],
                "",
                example,
            ]
        )

        func.__doc__ += example_section
        return func

    return _


def doc_format(**kwargs: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def _(func: Callable[P, T]) -> Callable[P, T]:
        if func.__doc__:
            func.__doc__ = func.__doc__.format(**kwargs)
        return func

    return _
