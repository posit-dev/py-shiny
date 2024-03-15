# This file should be copyable to the rsconnect-python package and usable without
# modification. The is_express_app() function should not be moved out of this file, and
# this file should not import anything else from shiny.

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Literal, cast

from .._docstring import no_example

__all__ = ("is_express_app",)


@no_example()
def is_express_app(app: str, app_dir: str | None) -> bool:
    """Detect whether an app file is a Shiny express app

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

    try:
        # Read the file, parse it, and look for any imports of shiny.express.
        with open(app_path, encoding="utf-8") as f:
            content = f.read()

        # Check for magic comment in the first 1000 characters
        forced_mode = find_magic_comment_mode(content[:1000])
        if forced_mode == "express":
            return True
        elif forced_mode == "core":
            return False

        tree = ast.parse(content, app_path)
        detector = DetectShinyExpressVisitor()
        detector.visit(tree)

    except Exception:
        return False

    return detector.found_shiny_express_import


class DetectShinyExpressVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.found_shiny_express_import = False

    def visit_Import(self, node: ast.Import) -> None:
        if any(alias.name == "shiny.express" for alias in node.names):
            self.found_shiny_express_import = True

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "shiny.express":
            self.found_shiny_express_import = True
        elif node.module == "shiny" and any(
            alias.name == "express" for alias in node.names
        ):
            self.found_shiny_express_import = True

    # Visit top-level nodes.
    def visit_Module(self, node: ast.Module) -> None:
        super().generic_visit(node)

    # Don't recurse into any nodes, so the we'll only ever look at top-level nodes.
    def generic_visit(self, node: ast.AST) -> None:
        pass


def find_magic_comment_mode(content: str) -> Literal["core", "express"] | None:
    """
    Look for a magic comment of the form "# shiny_mode: express" or "# shiny_mode:
    core".

    If a line of the form "# shiny_mode: x" is found, where "x" is not "express" or
    "core", then a message will be printed to stderr.

    Returns
    -------
    :
        `"express"` if Shiny Express comment is found, `"core"` if Shiny Core comment is
        found, and `None` if no magic comment is found.
    """
    m = re.search(r"^#[ \t]*shiny_mode:[ \t]*(\S*)[ \t]*$", content, re.MULTILINE)
    if m is not None:
        shiny_mode = cast(str, m.group(1))
        if shiny_mode in ("express", "core"):
            # The "type: ignore" is needed for mypy, which is used on some projects that
            # use duplicates of this code.
            return shiny_mode  # type: ignore
        else:
            print(f'Invalid shiny_mode: "{shiny_mode}"', file=sys.stderr)

    return None
