from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypeVar


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


def no_example(mode: Optional[Literal["express", "core"]] = None) -> Callable[[F], F]:
    """
    Prevent ``@add_example()`` from throwing an error about missing examples.

    Parameters
    ----------
    mode:
        If ``"express"``, ``@add_example()`` will not throw an error if the current
        mode is Express. If ``"core"``, ``@add_example()`` will not throw an error if
        the current mode is Core. If ``None``, ``@add_example()`` will not throw an
        error in either mode.
    """

    def decorator(func: F) -> F:
        current = getattr(func, "__no_example", [])
        if mode is None:
            current.extend(["express", "core"])
        else:
            current.append(mode)
        setattr(func, "__no_example", current)  # noqa: B010
        return func

    return decorator


# This class is used to mark docstrings when @add_example() is used, so that an error
# will be thrown if @doc_format() is used afterward. This is to avoid an error when
# the example contains curly braces -- the @doc_format() decorator will try to evaluate
# the code in {}.
class DocStringWithExample(str): ...


class ExampleWriter:
    def write_example(self, app_files: list[str]) -> str:
        app_file = app_files[0]
        with open(app_file) as f:
            code = f.read()

        return f"```.python\n{code.strip()}\n```\n"


example_writer = ExampleWriter()


def add_example(
    app_file: Optional[str] = None,
    ex_dir: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Add an example to the docstring of a function, method, or class.

    This decorator must, at the moment, be used on a function, method, or class whose
    ``__name__`` matches the name of directory under a ``api-examples/`` directory in
    the current or any parent directory.

    * Examples for the ``shiny`` package are in ``shiny/api-examples/``. We also place
      Express examples in this directory adjacent to their Core counterparts.
    * Examples for the ``shiny.experimental`` subpackage are in
      ``shiny/experimental/api-examples/``.

    Functions that can be used in Express or Core and whose canonical implementation is
    in the ``shiny`` package should have examples in ``shiny/api-examples``. In this
    case, the express variant should include an ``-express`` suffix and the core
    variation can be named with a ``-core`` suffix or ``app.py``.

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

        current_mode = os.getenv("SHINY_MODE", "core")
        if current_mode in getattr(func, "__no_example", []):
            return func

        func_dir = get_decorated_source_directory(func)
        fn_name = func.__name__

        if ex_dir is None:
            ex_dir_found = find_api_examples_dir(func_dir)

            if ex_dir_found is None:
                raise FileNotFoundError(
                    f"No example directory found for {fn_name} in {func_dir} or its parent directories."
                )
            example_dir = os.path.join(ex_dir_found, fn_name)
        else:
            example_dir = os.path.abspath(os.path.join(func_dir, ex_dir))

            if not os.path.exists(example_dir):
                raise FileNotFoundError(
                    f"Example directory '{example_dir}' does not exist for {fn_name}."
                )

        app_file_name = app_file or "app.py"
        try:
            example_file = app_choose_core_or_express(
                os.path.join(example_dir, app_file_name),
                mode="express" if "shiny/express/" in func_dir else None,
            )
        except ExampleNotFoundException as e:
            file = "shiny/" + func_dir.split("shiny/")[1]
            if "__code__" in dir(func):
                print(
                    f"::warning file={file},line={func.__code__.co_firstlineno}::{fn_name} - {e}"
                )
            else:
                print(f"::warning file={file}::{fn_name} - {e}")

            return func

        other_files: list[str] = []
        for abs_f in Path(example_dir).glob("**/*"):
            rel_f = abs_f.relative_to(example_dir)
            f = os.path.basename(abs_f)
            is_support_file = (
                os.path.isfile(abs_f)
                and f != app_file_name
                and f != "app.py"
                and f != ".DS_Store"
                and not f.startswith("app-")
                and not str(rel_f).startswith("__")
            )
            if is_support_file:
                other_files.append(str(abs_f))

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


def is_express_app(app_path: str) -> bool:
    # We can't use .shiny.express._is_express.is_express_app() here because that would
    # create a circular import.
    if not os.path.exists(app_path):
        return False

    with open(app_path) as f:
        for line in f:
            if "from shiny.express" in line:
                return True
            elif "import shiny.express" in line:
                return True
    return False


class ExampleNotFoundException(FileNotFoundError):
    def __init__(
        self,
        file_names: list[str] | str,
        dir: str,
        type: Optional[Literal["core", "express"]] = None,
    ) -> None:
        self.type = type or os.environ.get("SHINY_MODE", "core")
        self.file_names = [file_names] if isinstance(file_names, str) else file_names
        self.dir = dir

    def __str__(self):
        if self.type in ("core", "express"):
            # Capitalize first letter
            type = "a Shiny Express" if self.type == "express" else "a Shiny Core"
        else:
            type = "an"

        return (
            f"Could not find {type} example file named "
            + f"{' or '.join(self.file_names)} in {self.dir}."
        )


class ExpressExampleNotFoundException(ExampleNotFoundException):
    def __init__(
        self,
        file_names: list[str] | str,
        dir: str,
    ) -> None:
        super().__init__(file_names, dir, "express")


def app_choose_core_or_express(
    app_path: Optional[str] = None,
    mode: Optional[Literal["express", "core"]] = None,
) -> str:
    app_path = app_path or "app.py"

    if mode is None:
        mode_env = os.environ.get("SHINY_MODE", "core")
        mode = "express" if mode_env == "express" else "core"

    if mode == "express":
        if is_express_app(app_path):
            return app_path

        app_path = app_path.replace("-core.py", ".py")

        path, ext = os.path.splitext(app_path)
        app_path_express = f"{path}-express{ext}"

        if not is_express_app(app_path_express):
            raise ExpressExampleNotFoundException(
                [os.path.basename(app_path), os.path.basename(app_path_express)],
                os.path.dirname(app_path),
            )

        return app_path_express

    if os.path.basename(app_path) == "app.py" and not os.path.exists(app_path):
        app_path = app_path.replace("app.py", "app-core.py")

    if not os.path.exists(app_path):
        raise ExampleNotFoundException(
            os.path.basename(app_path),
            os.path.dirname(app_path),
        )

    return app_path


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
