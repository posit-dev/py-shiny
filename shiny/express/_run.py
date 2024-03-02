from __future__ import annotations

import ast
import os
import sys
from pathlib import Path
from typing import cast

from htmltools import Tag, TagList

from .._app import App
from .._docstring import no_example
from .._typing_extensions import NotRequired, TypedDict
from .._utils import import_module_from_path
from ..session import Inputs, Outputs, Session, get_current_session, session_context
from ..types import MISSING, MISSING_TYPE
from ._mock_session import ExpressMockSession
from ._recall_context import RecallContextManager
from .expressify_decorator._func_displayhook import _expressify_decorator_function_def
from .expressify_decorator._node_transformers import (
    DisplayFuncsTransformer,
    expressify_decorator_func_name,
)

__all__ = (
    "app_opts",
    "wrap_express_app",
)


@no_example()
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
        globals_file = file.parent / "globals.py"
        if globals_file.is_file():
            with session_context(None):
                import_module_from_path("globals", globals_file)

        mock_session = ExpressMockSession()
        with session_context(cast(Session, mock_session)):
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

            # Starting in Python 3.10 this could be traceback.print_exception(e)
            traceback.print_exception(*sys.exc_info())
            raise

    app_opts: AppOpts = {}

    www_dir = file.parent / "www"
    if www_dir.is_dir():
        app_opts["static_assets"] = {"/": www_dir}

    app_opts = _merge_app_opts(app_opts, mock_session.app_opts)
    app_opts = _normalize_app_opts(app_opts, file.parent)

    app = App(
        app_ui,
        express_server,
        **app_opts,  # pyright: ignore[reportArgumentType]
    )

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


class AppOpts(TypedDict):
    static_assets: NotRequired[dict[str, Path]]
    debug: NotRequired[bool]


@no_example()
def app_opts(
    static_assets: (
        str | os.PathLike[str] | dict[str, str | Path] | MISSING_TYPE
    ) = MISSING,
    debug: bool | MISSING_TYPE = MISSING,
):
    """
    Set App-level options in Shiny Express

    This function sets application-level options for Shiny Express. These options are
    the same as those from the :class:`shiny.App` constructor.

    Parameters
    ----------
    static_assets
        Static files to be served by the app. If this is a string or Path object, it
        must be a directory, and it will be mounted at `/`. If this is a dictionary,
        each key is a mount point and each value is a file or directory to be served at
        that mount point. In Shiny Express, if there is a `www` subdirectory of the
        directory containing the app file, it will automatically be mounted at `/`, even
        without needing to set the option here.
    debug
        Whether to enable debug mode.
    """

    # Store these options only if we're in the UI-rendering phase of Shiny Express.
    mock_session = get_current_session()
    if not isinstance(mock_session, ExpressMockSession):
        return

    if not isinstance(static_assets, MISSING_TYPE):
        if isinstance(static_assets, (str, os.PathLike)):
            static_assets = {"/": Path(static_assets)}

        # Convert string values to Paths. (Need new var name to help type checker.)
        static_assets_paths = {k: Path(v) for k, v in static_assets.items()}

        mock_session.app_opts["static_assets"] = static_assets_paths

    if not isinstance(debug, MISSING_TYPE):
        mock_session.app_opts["debug"] = debug


def _merge_app_opts(app_opts: AppOpts, app_opts_new: AppOpts) -> AppOpts:
    """
    Merge a set of app options into an existing set of app options. The values from
    `app_opts_new` take precedence. This will alter the original app_opts and return it.
    """

    # We can't just do a `app_opts.update(app_opts_new)` because we need to handle the
    # case where app_opts["static_assets"] and app_opts_new["static_assets"] are
    # dictionaries, and we need to merge those dictionaries.
    if "static_assets" in app_opts and "static_assets" in app_opts_new:
        app_opts["static_assets"].update(app_opts_new["static_assets"])
    elif "static_assets" in app_opts_new:
        app_opts["static_assets"] = app_opts_new["static_assets"].copy()

    if "debug" in app_opts_new:
        app_opts["debug"] = app_opts_new["debug"]

    return app_opts


def _normalize_app_opts(app_opts: AppOpts, parent_dir: Path) -> AppOpts:
    """
    Normalize the app options, ensuring that all paths in static_assets are absolute.
    Modifies the original in place.
    """
    if "static_assets" in app_opts:
        for mount_point, path in app_opts["static_assets"].items():
            if not path.is_absolute():
                path = parent_dir / path
            app_opts["static_assets"][mount_point] = path

    return app_opts
