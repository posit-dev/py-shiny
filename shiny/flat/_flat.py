# This file should only be imported by the user, not by any modules in Shiny, because it
# has side effects.

from __future__ import annotations

import ast
import contextlib
import os
import re
import sys
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any, Callable, ParamSpec, TypeVar, cast, overload

from htmltools import HTML, Tag, Tagifiable, TagList

from .. import render, ui
from .._app import App
from ..render.transformer import OutputRenderer
from ..session import Inputs, Outputs, Session
from ..ui import tags

__all__ = (
    "output_args",
    "suspend_display",
    "wrap_flat_app",
    "is_flat_app",
)

OT = TypeVar("OT")
P = ParamSpec("P")
R = TypeVar("R")


def wrap_flat_app(file: Path | None = None) -> App:
    """Wrap a flat Shiny app into a Shiny `App` object.

    Parameters
    ----------
    file
        The path to the file containing the flat Shiny application. If `None`, the
        `SHINY_FLAT_APP_FILE` environment variable is used.

    Returns
    -------
    :
        A `shiny.App` object.
    """
    if file is None:
        app_file = os.getenv("SHINY_FLAT_APP_FILE")
        if app_file is None:
            raise ValueError(
                "No app file was specified and the SHINY_FLAT_APP_FILE environment variable "
                "is not set."
            )
        file = Path(os.getcwd()) / app_file

    # TODO: title and lang
    app_ui = ui.page_fluid(ui.output_ui("__page__", style="display: contents;"))

    def flat_server(input: Inputs, output: Outputs, session: Session):
        dyn_ui = flat_run(file)

        @render.ui
        def __page__():
            return dyn_ui

    app = App(app_ui, flat_server)

    return app


def is_flat_app(app: str, app_dir: str | None) -> bool:
    if app_dir is not None:
        app_path = Path(app_dir) / app
    else:
        app_path = Path(app)

    if not app_path.exists():
        return False

    with open(app_path) as f:
        pattern = re.compile(
            "^(import shiny.flat)|(from shiny.flat import)|(from shiny import flat)"
        )

        for line in f:
            if pattern.match(line):
                return True

    return False


def flat_run(file: Path) -> TagList:
    with open(file) as f:
        content = f.read()

    tree = ast.parse(content, file)
    DisplayFuncsTransformer().visit(tree)

    collected_ui = TagList()

    def collect_ui(value: object):
        if isinstance(value, (Tag, TagList, Tagifiable)):
            collected_ui.append(value)
        elif hasattr(value, "_repr_html_"):
            collected_ui.append(HTML(value._repr_html_()))  # pyright: ignore
        else:
            if value is not None:
                collected_ui.append(tags.pre(repr(value)))

    sys.displayhook = collect_ui

    file_path = str(file.resolve())

    var_context: dict[str, object] = {
        "__file__": file_path,
        "__sys": sys,
    }

    # Execute each top-level node in the AST
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            exec(
                compile(ast.Module([node], type_ignores=[]), file_path, "exec"),
                var_context,
                var_context,
            )
            func = var_context[node.name]
            sys.displayhook(func)
        else:
            exec(
                compile(ast.Interactive([node], type_ignores=[]), file_path, "single"),
                var_context,
                var_context,
            )

    return collected_ui


class DisplayFuncsTransformer(ast.NodeTransformer):
    # Visit functions and async functions, inserting @sys.displayhook at the top of
    # their decorator lists

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.decorator_list.insert(
            0,
            set_loc(
                ast.Attribute(
                    value=set_loc(ast.Name(id="__sys", ctx=ast.Load()), node),
                    attr="displayhook",
                    ctx=ast.Load(),
                ),
                node,
            ),
        )
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> object:
        node.decorator_list.insert(
            0,
            set_loc(
                ast.Attribute(
                    value=set_loc(ast.Name(id="__sys", ctx=ast.Load()), node),
                    attr="displayhook",
                    ctx=ast.Load(),
                ),
                node,
            ),
        )
        return node

    # These are nodes that we WANT to descend into, looking for function definitions to
    # mangle. We specifically DON'T want to descend into the body of a function, because
    # only top-level function definitions should be displayed.
    #
    # For these nodes, we use the superclass's generic_visit, instead of our own, which
    # short-circuits the transformation.

    def visit_Module(self, node: ast.Module) -> object:
        return super().generic_visit(node)

    def visit_With(self, node: ast.With) -> object:
        return super().generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> object:
        return super().generic_visit(node)

    def visit_If(self, node: ast.If) -> object:
        return super().generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> object:
        return super().generic_visit(node)

    def visit_For(self, node: ast.For) -> object:
        return super().generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> object:
        return super().generic_visit(node)

    def visit_While(self, node: ast.While) -> object:
        return super().generic_visit(node)

    def visit_Try(self, node: ast.Try) -> object:
        return super().generic_visit(node)

    # For all other nodes, short-circuit the transformation--that is, don't recurse into
    # them.

    def generic_visit(self, node: ast.AST) -> ast.AST:
        return node


# ast.compile is insistent that all expressions have a lineno and col_offset
def set_loc(target: ast.expr, source: ast.AST) -> ast.expr:
    target.lineno = source.lineno
    target.col_offset = source.col_offset
    return target


def output_args(
    *args: Any, **kwargs: Any
) -> Callable[[OutputRenderer[OT]], OutputRenderer[OT]]:
    """Sets default UI arguments for a Shiny rendering function.

    Each Shiny render function (like :func:`~shiny.render.plot`) can display itself when
    declared within a Shiny inline-style application. In the case of
    :func:`~shiny.render.plot`, the :func:`~shiny.ui.output_plot` function is called
    implicitly to display the plot. Use the `@output_args` decorator to specify
    arguments to be passed to `output_plot` (or whatever the corresponding UI function
    is) when the render function displays itself.

    Parameters
    ----------
    *args
        Positional arguments to be passed to the UI function.
    **kwargs
        Keyword arguments to be passed to the UI function.

    Returns
    -------
    A decorator that sets the default UI arguments for a Shiny rendering function.
    """

    def wrapper(renderer: OutputRenderer[OT]) -> OutputRenderer[OT]:
        renderer.default_ui_args = args
        renderer.default_ui_kwargs = kwargs
        return renderer

    return wrapper


@overload
def suspend_display(fn: OutputRenderer[OT]) -> OutputRenderer[OT]:
    ...


@overload
def suspend_display(fn: Callable[P, R]) -> Callable[P, R]:
    ...


@overload
def suspend_display() -> AbstractContextManager[None]:
    ...


def suspend_display(
    fn: Callable[P, R] | OutputRenderer[OT] | None = None
) -> Callable[P, R] | OutputRenderer[OT] | AbstractContextManager[None]:
    """Suppresses the display of UI elements in various ways.

    If used as a context manager (`with suspend_display():`), it suppresses the display
    of all UI elements within the context block. (This is useful when you want to
    temporarily suppress the display of a large number of UI elements, or when you want
    to suppress the display of UI elements that are not directly under your control.)

    If used as a decorator (without parentheses) on a Shiny rendering function, it
    prevents that function from automatically outputting itself at the point of its
    declaration. (This is useful when you want to define the rendering logic for an
    output, but want to explicitly call a UI output function to indicate where and how
    it should be displayed.)

    If used as a decorator (without parentheses) on any other function, it turns
    Python's `sys.displayhook` into a no-op for the duration of the function call.

    Parameters
    ----------
    fn
        The function to decorate. If `None`, returns a context manager that suppresses
        the display of UI elements within the context block.

    Returns
    -------
    If `fn` is `None`, returns a context manager that suppresses the display of UI
    elements within the context block. Otherwise, returns a decorated version of `fn`.
    """

    if fn is None:
        return suspend_display_ctxmgr()

    # Special case for OutputRenderer; when we decorate those, we just mean "don't
    # display yourself"
    if isinstance(fn, OutputRenderer):
        fn.default_ui = null_ui
        return cast(Callable[P, R], fn)

    return suspend_display_ctxmgr()(fn)


@contextlib.contextmanager
def suspend_display_ctxmgr():
    oldhook = sys.displayhook
    sys.displayhook = null_displayhook
    try:
        yield
    finally:
        sys.displayhook = oldhook


def null_ui(id: str, *args: Any, **kwargs: Any) -> ui.TagList:
    return ui.TagList()


def null_displayhook(x: Any) -> None:
    pass
