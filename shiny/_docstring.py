from __future__ import annotations

import json
import os
from typing import Any, Callable, Literal, TypeVar

ex_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api-examples")

FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


# This class is used to mark docstrings when @add_example() is used, so that an error
# will be thrown if @doc_format() is used afterward. This is to avoid an error when
# the example contains curly braces -- the @doc_format() decorator will try to evaluate
# the code in {}.
class DocStringWithExample(str):
    ...


def add_example(
    directive: Literal[
        "shinyapp::",
        "shinylive-editor::",
        "code-block:: python",
        "cell::",
        "terminal::",
    ] = "shinylive-editor::",
    **options: object,
) -> Callable[[F], F]:
    """
    Add an example to the docstring of a function, method, or class.

    This decorator must, at the moment, be used on a function, method, or class whose
    ``__name__`` matches the name of directory under ``shiny/api-examples/``, and must
    also contain a ``app.py`` file in that directory.

    Parameters
    ----------
    directive
        A directive for rendering the example. This can be one of:
            - ``shinyapp``: A live shiny app (statically served via wasm).
            - ``code``: A python code snippet.
            - ``shinylive-editor``: A live shiny app with editor (statically served via wasm).
            - ``cell``: A executable Python cell.
            - ``terminal``: A minimal Python IDE
    **options
        Options for the directive. See docs/source/sphinxext/pyshinyapp.py for details.
    """

    def _(func: F) -> F:
        # To avoid a performance hit on `import shiny`, we only add examples to the
        # docstrings if this env variable is set (as it is in docs/source/conf.py).
        if os.getenv("SHINY_ADD_EXAMPLES") != "true":
            if func.__doc__ is not None:
                func.__doc__ = DocStringWithExample(func.__doc__)
            return func

        fn_name = func.__name__
        example_dir = os.path.join(ex_dir, fn_name)
        example_file = os.path.join(example_dir, "app.py")
        if not os.path.exists(example_file):
            raise ValueError(f"No example for {fn_name}")

        other_files: list[str] = []
        for f in os.listdir(example_dir):
            abs_f = os.path.join(example_dir, f)
            if os.path.isfile(abs_f) and f != "app.py":
                other_files.append(abs_f)

        if "files" not in options:
            options["files"] = json.dumps(other_files)

        if func.__doc__ is None:
            func.__doc__ = ""

        # How many leading spaces does the docstring start with?
        doc = func.__doc__.replace("\n", "")
        indent = " " * (len(doc) - len(doc.lstrip()))

        with open(example_file) as f:
            example = indent.join([" " * 4 + x for x in f.readlines()])

        # When rendering a standalone app, put the code above it (maybe this should be
        # handled by the directive itself?)
        example_prefix: list[str] = []
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
                *[f"    :{k}: {v}" for k, v in options.items()],
                "",
                example,
            ]
        )

        func.__doc__ += example_section
        func.__doc__ = DocStringWithExample(func.__doc__)
        return func

    return _


def doc_format(**kwargs: str) -> Callable[[F], F]:
    def _(func: F) -> F:
        if isinstance(func.__doc__, DocStringWithExample):
            raise ValueError(
                f"@doc_format() must be applied before @add_example() for {func.__name__}."
            )
        if func.__doc__:
            func.__doc__ = func.__doc__.format(**kwargs)
        return func

    return _
