from __future__ import annotations

import ast
import importlib.abc
import importlib.util
import sys
import types
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Literal, Mapping, Sequence, cast

from htmltools import Tag, TagList
from starlette.requests import Request

from .._app import App
from .._docstring import no_example
from .._typing_extensions import NotRequired, TypedDict
from .._utils import import_module_from_path
from ..bookmark._types import BookmarkStore
from ..session import Inputs, Outputs, Session, get_current_session, session_context
from ..types import MISSING, MISSING_TYPE
from ._is_express import find_magic_comment_mode
from ._recall_context import RecallContextManager
from ._stub_session import ExpressStubSession
from .expressify_decorator._func_displayhook import _expressify_decorator_function_def
from .expressify_decorator._node_transformers import (
    DisplayFuncsTransformer,
    expressify_decorator_func_name,
)

__all__ = (
    "app_opts",
    "wrap_express_app",
)

# Mapping from package name to file path of app. When running multiple concurrent apps
# (as is possible with shinylive), we need to give each one a unique package name.
package_filepath_map: dict[str, Path] = {}


@no_example()
def wrap_express_app(file: Path) -> App:
    """Wrap a Shiny Express mode app into a Shiny `App` object.

    This also creates a Python package for the app named something like
    `shiny_express_app_0`. This package is required for relative imports to work, as in
    `from . import utils`.

    Parameters
    ----------
    file
        The path to the file containing the Shiny express application.

    Returns
    -------
    :
        A :class:`shiny.App` object.
    """
    package_name = f"shiny_express_app_{len(package_filepath_map)}"
    package_filepath_map[package_name] = file

    # Importing the module triggers the ShinyExpressAppImportFinder and
    # ShinyExpressAppLoader.
    app_module = importlib.import_module(package_name)
    return app_module.app


# ======================================================================================
# Import hook to load Shiny Express app as a package
# ======================================================================================
class ShinyExpressAppImportFinder(importlib.abc.MetaPathFinder):
    def __init__(self):
        self.loaded_modules: dict[str, ModuleSpec] = {}

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: types.ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname in self.loaded_modules:
            return self.loaded_modules[fullname]

        if fullname in package_filepath_map:
            app_path = package_filepath_map[fullname]
            app_dir = str(app_path.parent)
            spec = importlib.util.spec_from_loader(
                fullname, ShinyExpressAppLoader(), origin=app_dir
            )
            if spec is None:
                return None

            spec.submodule_search_locations = [app_dir]
            self.loaded_modules[fullname] = spec
            return spec


class ShinyExpressAppLoader(importlib.abc.Loader):
    def create_module(self, spec: ModuleSpec):
        my_module = types.ModuleType(spec.name)
        return my_module

    def exec_module(self, module: types.ModuleType) -> None:
        module.app = create_express_app(  # pyright: ignore[reportAttributeAccessIssue]
            package_filepath_map[module.__name__], module.__name__
        )


sys.meta_path.insert(0, ShinyExpressAppImportFinder())
# ======================================================================================


# This is invoked from the ShinyExpressAppLoader.exec_module() method above. It creates
# the App object from the Shiny Express app file.
@no_example()
def create_express_app(file: Path, package_name: str) -> App:

    file = file.resolve()

    stub_session = ExpressStubSession()
    try:
        globals_file = file.parent / "globals.py"
        if globals_file.is_file():
            with session_context(None):
                import_module_from_path("globals", globals_file)

        with session_context(stub_session):
            # We tagify here, instead of waiting for the App object to do it when it wraps
            # the UI in a HTMLDocument and calls render() on it. This is because
            # AttributeErrors can be thrown during the tagification process, and we need to
            # catch them here and convert them to a different type of error, because uvicorn
            # specifically catches AttributeErrors and prints an error message that is
            # misleading for Shiny Express. https://github.com/posit-dev/py-shiny/issues/937
            app_ui = run_express(file, package_name).tagify()

    except AttributeError as e:
        raise RuntimeError(e) from e

    express_bookmark_store = stub_session.app_opts.get("bookmark_store", "disable")
    if express_bookmark_store != "disable":
        # If bookmarking is enabled, wrap UI in function to automatically leverage UI
        # functions to restore their values
        def app_ui_wrapper(request: Request):
            # Stub session used to pass `app_opts()` checks.
            with session_context(ExpressStubSession()):
                return run_express(file, package_name).tagify()

        app_ui = app_ui_wrapper

    def express_server(input: Inputs, output: Outputs, session: Session):
        try:
            run_express(file, package_name)

        except Exception:
            import traceback

            # Starting in Python 3.10 this could be traceback.print_exception(e)
            traceback.print_exception(*sys.exc_info())
            raise

    app_opts: AppOpts = {}

    www_dir = file.parent / "www"
    if www_dir.is_dir():
        app_opts["static_assets"] = {"/": www_dir}

    app_opts = _merge_app_opts(app_opts, stub_session.app_opts)
    app_opts = _normalize_app_opts(app_opts, file.parent)

    app = App(
        app_ui,
        express_server,
        **app_opts,  # pyright: ignore[reportArgumentType]
    )

    return app


def run_express(file: Path, package_name: str | None = None) -> Tag | TagList:
    """
    Run the code in a Shiny Express app file and return the UI. This is to be run in
    both the UI-rendering phase and the server-rendering phase of a Shiny Express app.
    When used in the server-rendering phase, the returned UI should simply be ignored.

    Parameters
    ----------
    file
        The path to the file containing the Shiny Express application.
    package_name
        The name of the package for the app. This is generated by `wrap_express_app()`
        and should be something like "shiny_express_app_0". The purpose of this is to
        allow relative imports in the app code.
    """
    with open(file, encoding="utf-8") as f:
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
            "__name__": "app",
            "__package__": package_name,
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
                    compile(ast.Interactive([node]), file_path, "single"),
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
        # which is a shiny.App object, the user probably made a mistake. (But if there's
        # a magic comment to force it into Express mode, don't raise, because that means
        # the user should know what they're doing.)
        if (
            "app" in var_context
            and isinstance(var_context["app"], App)
            and find_magic_comment_mode(content[:1000]) is None
        ):
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


_top_level_recall_context_manager: RecallContextManager[Tag] | None = None


def reset_top_level_recall_context_manager() -> None:
    from .ui._page import page_auto_cm

    global _top_level_recall_context_manager
    _top_level_recall_context_manager = page_auto_cm()


def get_top_level_recall_context_manager() -> RecallContextManager[Tag]:
    if _top_level_recall_context_manager is None:
        raise RuntimeError("No top-level recall context manager has been set.")

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
    bookmark_store: NotRequired[BookmarkStore]
    debug: NotRequired[bool]


@no_example()
def app_opts(
    *,
    static_assets: str | Path | Mapping[str, str | Path] | MISSING_TYPE = MISSING,
    bookmark_store: Literal["url", "server", "disable"] | MISSING_TYPE = MISSING,
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
    bookmark_store
        Where to store the bookmark state.

        * `"url"`: Encode the bookmark state in the URL.
        * `"server"`: Store the bookmark state on the server.
        * `"disable"`: Disable bookmarking.
    debug
        Whether to enable debug mode.
    """

    stub_session = get_current_session()

    if stub_session is None:
        # We can get here if a Shiny Core app, or if we're in the UI rendering phase of
        # a Quarto-Shiny dashboard.
        raise RuntimeError(
            "express.app_opts() can only be used in a standalone Shiny Express app."
        )

    # Store these options only if we're in the UI-rendering phase of Shiny Express.
    if not isinstance(stub_session, ExpressStubSession):
        return

    if not isinstance(static_assets, MISSING_TYPE):
        if isinstance(static_assets, (str, Path)):
            static_assets = {"/": Path(static_assets)}

        # Convert string values to Paths. (Need new var name to help type checker.)
        static_assets_paths = {k: Path(v) for k, v in static_assets.items()}

        stub_session.app_opts["static_assets"] = static_assets_paths

    if not isinstance(bookmark_store, MISSING_TYPE):
        stub_session.app_opts["bookmark_store"] = bookmark_store

    if not isinstance(debug, MISSING_TYPE):
        stub_session.app_opts["debug"] = debug


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

    if "bookmark_store" in app_opts_new:
        app_opts["bookmark_store"] = app_opts_new["bookmark_store"]

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
