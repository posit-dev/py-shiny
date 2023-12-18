from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path
from typing import cast

from htmltools import Tag, TagList

from .. import ui
from .._app import App
from ..session import Inputs, Outputs, Session
from ._recall_context import RecallContextManager
from .display_decorator._func_displayhook import _display_decorator_function_def
from .display_decorator._node_transformers import (
    DisplayFuncsTransformer,
    display_decorator_func_name,
)

__all__ = ("wrap_express_app",)

_DEFAULT_PAGE_FUNCTION = ui.page_fixed


def wrap_express_app(file: Path) -> App:
    """Wrap a Shiny Express mode app into a Shiny `App` object.

    Parameters
    ----------
    file
        The path to the file containing the Shiny express application.

    Returns
    -------
    :
        A `shiny.App` object.
    """
    logging.getLogger("uvicorn.error").warning(
        "Detected Shiny Express app. please note that Shiny Express is still in "
        "development and the API is subject to change!"
    )

    app_ui = run_express(file)

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
            display_decorator_func_name: _display_decorator_function_def,
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
_top_level_recall_context_manager_has_been_replaced = False


def reset_top_level_recall_context_manager():
    global _top_level_recall_context_manager
    global _top_level_recall_context_manager_has_been_replaced
    _top_level_recall_context_manager = RecallContextManager(_DEFAULT_PAGE_FUNCTION)
    _top_level_recall_context_manager_has_been_replaced = False


def get_top_level_recall_context_manager():
    return _top_level_recall_context_manager


def replace_top_level_recall_context_manager(
    cm: RecallContextManager[Tag],
    force: bool = False,
) -> RecallContextManager[Tag]:
    """
    Replace the current top level RecallContextManager with another one.

    This transfers the `args` and `kwargs` from the previous RecallContextManager to the
    new one. Normally it will only have an effect the first time it's run; it only
    replace the previous one if has not already been replaced. To override this
    behavior, this use `force=True`.

    Parameters
    ----------
    cm
        The RecallContextManager to replace the previous one.
    force
        If `False` (the default) and the top level RecallContextManager has already been
        replaced, return with no chnages. If `True`, this will aways replace.

    Returns
    -------
    :
        The previous top level RecallContextManager.
    """
    global _top_level_recall_context_manager
    global _top_level_recall_context_manager_has_been_replaced

    old_cm = _top_level_recall_context_manager

    if force is False and _top_level_recall_context_manager_has_been_replaced:
        return old_cm

    args = old_cm.args.copy()
    args.extend(cm.args)
    cm.args = args

    kwargs = old_cm.kwargs.copy()
    kwargs.update(cm.kwargs)
    cm.kwargs = kwargs

    old_cm.__exit__(BaseException, None, None)
    cm.__enter__()
    _top_level_recall_context_manager = cm
    _top_level_recall_context_manager_has_been_replaced = True

    return old_cm
