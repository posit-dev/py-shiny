from __future__ import annotations

import os
import sys
from typing import Any, Callable, Optional, TypeVar


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


def ex_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "api-examples")


FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


# This class is used to mark docstrings when @add_example() is used, so that an error
# will be thrown if @doc_format() is used afterward. This is to avoid an error when
# the example contains curly braces -- the @doc_format() decorator will try to evaluate
# the code in {}.
class DocStringWithExample(str):
    ...


class ExampleWriterRegistry:
    def __init__(self):
        self._writer = None

    def set_writer(self, func: F) -> F:
        self._writer = func
        return func

    def write_example(self, app_files: list[str], **kwargs: dict[str, Any]) -> str:
        if self._writer is None:
            return self.default_writer(app_files)
        return self._writer(app_files, **kwargs)

    def default_writer(self, app_files: list[str]) -> str:
        app_file = app_files[0]
        with open(app_file) as f:
            code = f.read()

        return f"```.python\n{code.strip()}\n```\n"


example_writer = ExampleWriterRegistry()


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

        nonlocal app_file
        nonlocal ex_dir

        if ex_dir is None:
            func_dir = get_decorated_source_directory(func)
            ex_dir = find_api_examples_dir(func_dir)

            if ex_dir is None:
                raise ValueError(
                    f"No example directory found for {func.__name__} in {func_dir} or its parent directories."
                )

        fn_name = func.__name__
        example_dir = os.path.join(ex_dir, fn_name)
        example_file = os.path.join(example_dir, app_file)
        if not os.path.exists(example_file):
            raise ValueError(f"No example for {fn_name}")

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
        if not isinstance(func.__doc__, DocStringWithExample):
            func.__doc__ += nl_indent + "Examples"
            func.__doc__ += nl_indent + "--------"

        # Add the example to the docstring
        func.__doc__ += nl_indent * 2
        func.__doc__ += nl_indent.join(example_lines)
        func.__doc__ = DocStringWithExample(func.__doc__)
        return func

    return _


def get_decorated_source_directory(func: F) -> str:
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


if os.environ.get("IN_QUARTODOC") == "true":
    try:
        import shinylive

        shinylive.__version__
    except ModuleNotFoundError:
        import warnings

        warnings.warn(
            "shinylive not installed, cannot add shinylive examples.", stacklevel=2
        )
        pass

    SHINYLIVE_CODE_TEMPLATE = """
```{{shinylive-python}}
#| standalone: true
#| components: [editor, viewer]
#| layout: vertical
#| viewerHeight: 400

{0}
```
"""

    @example_writer.set_writer
    def write_shinylive_example(app_files: list[str]) -> str:
        import shinylive

        app_file = app_files.pop(0)
        bundle = shinylive._url.create_shinylive_bundle_file(
            app_file, app_files, language="py"
        )
        code = shinylive._url.create_shinylive_chunk_contents(bundle)

        return SHINYLIVE_CODE_TEMPLATE.format(code.strip())
