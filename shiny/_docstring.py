from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar


def find_api_examples_dir(start_dir: str) -> Optional[str]:
    current_dir = os.path.abspath(start_dir)
    while True:
        api_examples_dir = os.path.join(current_dir, "api-examples")
        if os.path.isdir(api_examples_dir):
            return api_examples_dir
        root_files = ["setup.cfg", "pyproject.toml"]
        dir_files = os.listdir(current_dir)
        if any(rf in dir_files for rf in root_files):
            break  # Reached the package root directory
        if current_dir == os.path.dirname(current_dir):
            break  # Reached the global root directory
        current_dir = os.path.dirname(current_dir)
    return None


FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


def no_example(func: F) -> F:
    return func


# This class is used to mark docstrings when @add_example() is used, so that an error
# will be thrown if @doc_format() is used afterward. This is to avoid an error when
# the example contains curly braces -- the @doc_format() decorator will try to evaluate
# the code in {}.
class DocStringWithExample(str):
    ...


class ExampleWriter:
    def write_example(self, app_files: list[str]) -> str:
        app_file = app_files[0]
        with open(app_file) as f:
            code = f.read()

        return f"```.python\n{code.strip()}\n```\n"


example_writer = ExampleWriter()


def add_example(
    app_file: str = "app.py",
    ex_dir: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Add an example to the docstring of a function, method, or class.

    This decorator must, at the moment, be used on a function, method, or class whose
    ``__name__`` matches the name of directory under a ``api-examples/`` directory in
    the current or any parent directory.

    Parameters
    ----------
    app_file:
        The primary app file to use for the example. This allows you to have multiple
        example files for a single function or to use a different file name than
        ``app.py``. Support files _cannot_ be named ``app.py`` or start with ``app-``,
        as these files will never be included in the example.
    ex_dir:
        The directory containing the example. If not specified, ``add_example()`` will
        find a directory named after the current function in the first ``api-examples/``
        directory it finds in the current directory or its parent directories.
    """

    def _(func: F) -> F:
        # To avoid a performance hit on `import shiny`, we only add examples to the
        # docstrings if this env variable is set (as it is in `make quartodoc`).
        if os.getenv("SHINY_ADD_EXAMPLES") != "true":
            if func.__doc__ is not None:
                func.__doc__ = DocStringWithExample(func.__doc__)
            return func

        func_dir = get_decorated_source_directory(func)
        fn_name = func.__name__

        if ex_dir is None:
            ex_dir_found = find_api_examples_dir(func_dir)

            if ex_dir_found is None:
                raise ValueError(
                    f"No example directory found for {fn_name} in {func_dir} or its parent directories."
                )
            example_dir = os.path.join(ex_dir_found, fn_name)
        else:
            example_dir = os.path.join(func_dir, ex_dir)

        example_file = os.path.join(example_dir, app_file)
        if not os.path.exists(example_file):
            raise ValueError(
                f"No example for {fn_name} found in '{os.path.abspath(example_dir)}'."
            )

        other_files: list[str] = []
        for f in os.listdir(example_dir):
            abs_f = os.path.join(example_dir, f)
            is_support_file = (
                os.path.isfile(abs_f)
                and f != app_file
                and f != "app.py"
                and not f.startswith("app-")
                and not f.startswith("__")
            )
            if is_support_file:
                other_files.append(abs_f)

        if func.__doc__ is None:
            func.__doc__ = ""

        example = example_writer.write_example([example_file, *other_files])
        example_lines = example.split("\n")

        # How many leading spaces does the docstring start with?
        doc = func.__doc__.replace("\n", "")
        indent = " " * (len(doc) - len(doc.lstrip()))
        nl_indent = "\n" + indent

        # Add example header if not already present
        # WARNING: All `add_example()` calls must be coalesced.
        # Note that we're using numpydoc-style headers here, quartodoc will handle
        # converting them to markdown headers.
        if isinstance(func.__doc__, DocStringWithExample):
            ex_header = "Examples" + nl_indent + "--------"
            before, after = func.__doc__.split(ex_header, 1)
            func.__doc__ = before + ex_header
        else:
            func.__doc__ += nl_indent + "Examples"
            func.__doc__ += nl_indent + "--------"
            after = None

        # Insert the example under the Examples heading
        func.__doc__ += nl_indent * 2
        func.__doc__ += nl_indent.join(example_lines)
        if after is not None:
            func.__doc__ += after

        func.__doc__ = DocStringWithExample(func.__doc__)
        return func

    return _


def get_decorated_source_directory(func: FuncType) -> str:
    if hasattr(func, "__module__"):
        path = os.path.abspath(str(sys.modules[func.__module__].__file__))
    else:
        path = os.path.abspath(func.__code__.co_filename)

    return os.path.dirname(path)


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


if not TYPE_CHECKING and os.environ.get("IN_QUARTODOC") == "true":
    # When running in quartodoc, we use shinylive to embed the examples in the docs.
    # This part is hidden from the typechecker because shinylive is not a direct
    # dependency of shiny and we only need this section when building the docs.
    try:
        from shinylive import ShinyliveApp
    except ImportError:
        raise RuntimeError(
            "Please install the latest version of shinylive to build the docs."
        )
    except ModuleNotFoundError:
        raise RuntimeError("Please install shinylive to build the docs.")

    class ShinyliveExampleWriter(ExampleWriter):
        def write_example(self, app_files: list[str]) -> str:
            app_file = app_files.pop(0)
            app = ShinyliveApp.from_local(app_file, app_files, language="py")

            return app.to_chunk(layout="vertical", viewer_height=400)

    example_writer = ShinyliveExampleWriter()
