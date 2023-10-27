from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

from htmltools import Tag, TagList

from .. import render, ui
from .._app import App
from ..session import Inputs, Outputs, Session
from ._recall_context import RecallContextManager

__all__ = (
    "wrap_express_app",
    "is_express_app",
)


def wrap_express_app(file: Path | None = None) -> App:
    """Wrap a Shiny express-mode app into a Shiny `App` object.

    Parameters
    ----------
    file
        The path to the file containing the Shiny express application. If `None`, the
        `SHINY_EXPRESS_APP_FILE` environment variable is used.

    Returns
    -------
    :
        A `shiny.App` object.
    """
    if file is None:
        app_file = os.getenv("SHINY_EXPRESS_APP_FILE")
        if app_file is None:
            raise ValueError(
                "No app file was specified and the SHINY_EXPRESS_APP_FILE environment variable "
                "is not set."
            )
        file = Path(os.getcwd()) / app_file

    # TODO: title and lang
    app_ui = ui.page_output("__page__")

    def express_server(input: Inputs, output: Outputs, session: Session):
        dyn_ui = run_express(file)

        @render.ui
        def __page__():
            return dyn_ui

    app = App(app_ui, express_server)

    return app


def is_express_app(app: str, app_dir: str | None) -> bool:
    """ "Detect whether an app file is a Shiny express app

    Parameters
    ----------
    app
        App filename, like "app.py". It may be a relative path or absolute path.
    app_dir
        Directory containing the app file. If this is `None`, then `app` must be an
        absolute path.

    Returns
    -------
    :
        `True` if it is a Shiny express app, `False` otherwise.
    """
    if not app.lower().endswith(".py"):
        return False

    if app_dir is not None:
        app_path = Path(app_dir) / app
    else:
        app_path = Path(app)

    if not app_path.exists():
        return False

    # Read the file, parse it, and look for any imports of shiny.express.
    with open(app_path) as f:
        content = f.read()
    tree = ast.parse(content, app_path)
    detector = DetectShinyExpressVisitor()
    detector.visit(tree)

    return detector.found_shiny_express_import


def run_express(file: Path) -> Tag | TagList:
    with open(file) as f:
        content = f.read()

    tree = ast.parse(content, file)
    DisplayFuncsTransformer().visit(tree)

    ui_result: Tag | TagList = TagList()

    def set_result(x: object):
        nonlocal ui_result
        ui_result = x

    sys.displayhook = set_result

    reset_top_level_recall_context_manager()
    get_top_level_recall_context_manager().__enter__()

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

    get_top_level_recall_context_manager().__exit__(None, None, None)
    return ui_result


_top_level_recall_context_manager: RecallContextManager[Tag]
_top_level_recall_context_manager_has_been_replaced = False


def reset_top_level_recall_context_manager():
    global _top_level_recall_context_manager
    global _top_level_recall_context_manager_has_been_replaced
    _top_level_recall_context_manager = RecallContextManager(ui.page_fluid)
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


class DetectShinyExpressVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.found_shiny_express_import = False

    def visit_Import(self, node: ast.Import):
        if any(alias.name == "shiny.express" for alias in node.names):
            self.found_shiny_express_import = True

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "shiny.express":
            self.found_shiny_express_import = True
        elif node.module == "shiny" and any(
            alias.name == "express" for alias in node.names
        ):
            self.found_shiny_express_import = True

    # Visit top-level nodes.
    def visit_Module(self, node: ast.Module):
        super().generic_visit(node)

    # Don't recurse into any nodes, so the we'll only ever look at top-level nodes.
    def generic_visit(self, node: ast.AST):
        pass


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
