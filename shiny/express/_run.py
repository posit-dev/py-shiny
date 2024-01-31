from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import cast

from htmltools import Tag, TagList

from .._app import App
from ..session import Inputs, Outputs, Session, session_context
from ._mock_session import MockSession
from ._recall_context import RecallContextManager
from .expressify_decorator._func_displayhook import _expressify_decorator_function_def
from .expressify_decorator._node_transformers import (
    DisplayFuncsTransformer,
    expressify_decorator_func_name,
)

__all__ = ("wrap_express_app",)


def wrap_express_app(file: Path) -> App:
    """Wrap a Shiny Express mode app into a Shiny `App` object.

    Parameters
    ----------
    file
        The path to the file containing the Shiny express application.

    Returns
    -------
    :
        A :class:`shiny.App` object.
    """
    try:
        with session_context(cast(Session, MockSession())):
            # We tagify here, instead of waiting for the App object to do it when it wraps
            # the UI in a HTMLDocument and calls render() on it. This is because
            # AttributeErrors can be thrown during the tagification process, and we need to
            # catch them here and convert them to a different type of error, because uvicorn
            # specifically catches AttributeErrors and prints an error message that is
            # misleading for Shiny Express. https://github.com/posit-dev/py-shiny/issues/937
            app_ui = run_express(file).tagify()

    except AttributeError as e:
        raise RuntimeError(e) from e

    def express_server(input: Inputs, output: Outputs, session: Session):
        try:
            run_express(file)

        except Exception:
            import traceback

            traceback.print_exception(*sys.exc_info())
            raise

    app = App(app_ui, express_server)

    return app


def run_express(file: Path) -> Tag | TagList:
    with open(file) as f:
        content = f.read()

    tree = ast.parse(content, file)
    tree = DisplayFuncsTransformer().visit(tree)
    tree = ast.fix_missing_locations(tree)

    ui_result: Tag | TagList = TagList()

    def set_result(x: object):
        nonlocal ui_result
        ui_result = cast(Tag, x)

    prev_displayhook = sys.displayhook
    sys.displayhook = set_result

    try:
        reset_top_level_recall_context_manager()
        get_top_level_recall_context_manager().__enter__()

        file_path = str(file.resolve())

        var_context: dict[str, object] = {
            "__file__": file_path,
            expressify_decorator_func_name: _expressify_decorator_function_def,
            "input": InputNotImportedShim(),
        }

        # Execute each top-level node in the AST
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                exec(
                    compile(ast.Module([node], type_ignores=[]), file_path, "exec"),
                    var_context,
                    var_context,
                )
            else:
                exec(
                    compile(
                        ast.Interactive([node], type_ignores=[]), file_path, "single"
                    ),
                    var_context,
                    var_context,
                )

        # When we called the function to get the top level recall context manager, we didn't
        # store the result in a variable and re-use that variable here. That is intentional,
        # because during the evaluation of the app code,
        # replace_top_level_recall_context_manager() may have been called, which swaps
        # out the context manager, and it's the new one that we need to exit here.
        get_top_level_recall_context_manager().__exit__(None, None, None)

        # If we're running as an Express app but there's also a top-level item named app
        # which is a shiny.App object, the user probably made a mistake.
        if "app" in var_context and isinstance(var_context["app"], App):
            raise RuntimeError(
                "This looks like a Shiny Express app because it imports shiny.express, "
                "but it also looks like a Shiny Core app because it has a variable named "
                "`app` which is a shiny.App object. Remove either the shiny.express import, "
                "or the app=App()."
            )

        return ui_result

    except AttributeError as e:
        # Need to catch AttributeError and convert to a different type of error, because
        # uvicorn specifically catches AttributeErrors and prints an error message that
        # is helpful for normal ASGI apps, but misleading in the case of Shiny Express.
        raise RuntimeError(e) from e

    finally:
        sys.displayhook = prev_displayhook


_top_level_recall_context_manager: RecallContextManager[Tag]


def reset_top_level_recall_context_manager() -> None:
    from .ui._page import page_auto_cm

    global _top_level_recall_context_manager
    _top_level_recall_context_manager = page_auto_cm()


def get_top_level_recall_context_manager() -> RecallContextManager[Tag]:
    return _top_level_recall_context_manager


class InputNotImportedShim:
    # This is a dummy class that is used to provide a helpful error message when the
    # user tries to access `input.x` but forgot to import `input`. If they do that, then
    # it would get the builtin `input` function, and print an unhelpful error message:
    #   RuntimeError: 'builtin_function_or_method' object has no attribute 'x'
    # This class provides an error message that is more helpful.
    def __getattr__(self, name: str):
        raise AttributeError(
            "Tried to access `input`, but it was not imported. "
            "Perhaps you need `from shiny.express import input`?"
        )
