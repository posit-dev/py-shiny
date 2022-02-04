import importlib
import importlib.util
import os
import sys
import types
import click
import typing

import uvicorn
import uvicorn.config

import shiny

__all__ = ["main", "run"]


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("app", default="app:app")
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port.",
    show_default=True,
)
@click.option(
    "--debug", is_flag=True, default=False, help="Enable debug mode.", hidden=True
)
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload.")
@click.option(
    "--ws-max-size",
    type=int,
    default=16777216,
    help="WebSocket max size message in bytes",
    show_default=True,
)
@click.option(
    "--log-level",
    type=click.Choice(list(uvicorn.config.LOG_LEVELS.keys())),
    default=None,
    help="Log level. [default: info]",
    show_default=True,
)
@click.option(
    "--app-dir",
    default=".",
    show_default=True,
    help="Look for APP in the specified directory, by adding this to the PYTHONPATH."
    " Defaults to the current working directory.",
)
def run(
    app: typing.Union[str, shiny.ShinyApp],
    host: str,
    port: int,
    debug: bool,
    reload: bool,
    ws_max_size: int,
    log_level: str,
    app_dir: str,
) -> None:
    """Starts a Shiny app. Press Ctrl+C (or Ctrl+Break on Windows) to stop.

    The APP argument indicates where the Shiny app should be loaded from. You have
    several options for specifying this:

    \b
    - No APP argument; `shiny run` will look for app.py in the current directory.
    - A module name to load. It should have an `app` attribute.
    - A "<module>:<attribute>" string. Useful when you named your Shiny app
      something other than `app`, or if there are multiple apps in a single
      module.
    - A relative path to a Python file.
    - A relative path to a Python directory (it must contain an app.py file).
    - A "<path-to-file-or-dir>:<attribute>" string.

    \b
    Examples
    ========
    shiny run
    shiny run mypackage.mymodule
    shiny run mypackage.mymodule:app
    shiny run mydir
    shiny run mydir/myapp.py
    shiny run mydir/myapp.py:app
    """

    if isinstance(app, str):
        app = resolve_app(app, app_dir)

    uvicorn.run(
        app,  # type: ignore
        host=host,
        port=port,
        debug=debug,
        reload=reload,
        ws_max_size=ws_max_size,
        log_level=log_level,
        # DON'T pass app_dir, as uvicorn.run didn't support it until recently
        # app_dir=app_dir,
    )


def resolve_app(app: str, app_dir: typing.Optional[str]) -> typing.Any:
    # The `app` parameter can be:
    #
    # - A module:attribute name
    # - An absolute or relative path to a:
    #   - .py file (look for app inside of it)
    #   - directory (look for app:app inside of it)
    # - A module name (look for :app) inside of it

    module, _, attr = app.partition(":")
    if not module:
        raise ImportError("The APP parameter cannot start with ':'.")
    if not attr:
        attr = "app"

    if app_dir is not None:
        sys.path.insert(0, app_dir)

    instance = try_import_module(module)
    if not instance:
        # It must be a path
        path = os.path.normpath(module)
        if path.startswith("../") or path.startswith("..\\"):
            raise ImportError(
                "The APP parameter cannot refer to a parent directory ('..'). "
                "Either change the working directory to a parent of the app, "
                "or use the --app-dir option to specify a different starting "
                "directory to search from."
            )
        fullpath = os.path.normpath(os.path.join(app_dir or ".", module))
        if not os.path.exists(fullpath):
            raise ImportError(f"Could not find the module or path '{module}'")
        if os.path.isdir(fullpath):
            path = os.path.join(path, "app.py")
            fullpath = os.path.join(fullpath, "app.py")
            if not os.path.exists(fullpath):
                raise ImportError(
                    f"The directory '{fullpath}' did not include an app.py file"
                )
        module = path.removesuffix(".py").replace("/", ".").replace("\\", ".")
        instance = try_import_module(module)
        if not instance:
            raise ImportError(f"Could not find the module '{module}'")

    return getattr(instance, attr)


def try_import_module(module: str) -> typing.Optional[types.ModuleType]:
    try:
        if importlib.util.find_spec(module):
            return importlib.import_module(module)
        return None
    except ModuleNotFoundError:
        # find_spec throws this when the module contains both '/' and '.' characters
        return None
    except ImportError:
        # find_spec throws this when the module starts with "."
        return None
