from __future__ import annotations

import re
from pathlib import Path

from htmltools import HTML, Tag, Tagifiable, TagList

from . import render
from ._app import App
from .session import Inputs, Outputs, Session
from .ui import output_ui, page_fluid


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
    import ast
    import sys

    with open(file) as f:
        content = f.read()

    tree = ast.parse(content, file)

    collected_ui = TagList()

    def collect_ui(value: object):
        if isinstance(value, (Tag, TagList, Tagifiable)):
            collected_ui.append(value)
        elif hasattr(value, "_repr_html_"):
            # TODO: Make render functions have a tagify method
            collected_ui.append(HTML(value._repr_html_()))

    sys.displayhook = collect_ui

    var_context: dict[str, object] = {}

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
