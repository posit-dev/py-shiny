from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from htmltools import HTML, Tag, Tagifiable, TagList

from . import render
from ._app import App
from .session import Inputs, Outputs, Session
from .ui import output_ui, page_fluid, tags


def is_flat_app(app: str, app_dir: str | None) -> bool:
    if app_dir is not None:
        app_path = Path(app_dir) / app
    else:
        app_path = Path(app)

    if not app_path.exists():
        raise ValueError(f"App file at {app_path} does not exist")

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
            collected_ui.append(tags.pre(repr(value)))

    sys.displayhook = collect_ui

    var_context: dict[str, object] = {}
    var_context["__sys"] = sys

    # Execute each top-level node in the AST
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            exec(
                compile(ast.Module([node], type_ignores=[]), "<ast>", "exec"),
                var_context,
                var_context,
            )
            func = var_context[node.name]
            sys.displayhook(func)
        else:
            exec(
                compile(ast.Interactive([node], type_ignores=[]), "<ast>", "single"),
                var_context,
                var_context,
            )

    return collected_ui


def create_flat_app(file: Path) -> App:
    # TODO: title and lang
    app_ui = page_fluid(output_ui("__page__", style="display: contents;"))

    def flat_server(input: Inputs, output: Outputs, session: Session):
        dyn_ui = flat_run(file)

        @render.ui
        def __page__():
            return dyn_ui

    app = App(app_ui, flat_server)

    return app


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
