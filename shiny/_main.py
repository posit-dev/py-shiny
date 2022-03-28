import importlib
import importlib.util
import os
import sys
import types
from typing import Optional, Union

import click
import uvicorn
import uvicorn.config

import shiny


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
    app: Union[str, shiny.App],
    host: str,
    port: int,
    debug: bool,
    reload: bool,
    ws_max_size: int,
    log_level: str,
    app_dir: str,
) -> None:
    return run_app(
        app,
        host=host,
        port=port,
        debug=debug,
        reload=reload,
        ws_max_size=ws_max_size,
        log_level=log_level,
        app_dir=app_dir,
    )


def run_app(
    app: Union[str, shiny.App] = "app:app",
    host: str = "127.0.0.1",
    port: int = 8000,
    debug: bool = False,
    reload: bool = False,
    ws_max_size: int = 16777216,
    log_level: Optional[str] = None,
    app_dir: Optional[str] = ".",
) -> None:
    """
    Starts a Shiny app. Press ``Ctrl+C`` (or ``Ctrl+Break`` on Windows) to stop.

    Parameters
    ----------
    app
        The app to run. The default, ``app:app``, represents the "usual" case where the
        application is named ``app`` inside a ``app.py`` file within the current working
        directory. In other cases, the app location can be specified as a
        ``<module>:<attribute>`` string where the ``:<attribute>`` is only necessary if
        the application is named something other than ``app``. Note that ``<module>``
        can be relative path to a ``.py`` file or a directory (with an ``app.py`` file
        inside it); and in this case, the relative path is resolved relative to the
        ``app_dir`` directory.
    host
        The address that the app should listen on.
    port
        The port that the app should listen on.
    debug
        Enable debug mode.
    reload
        Enable auto-reload.
    ws_max_size
        WebSocket max size message in bytes.
    log_level
        Log level.
    app_dir
        Look for ``app`` under this directory (by adding this to the ``PYTHONPATH``).

    Tip
    ---
    The ``shiny run`` command-line interface (which comes installed with Shiny) provides
    the same functionality as this function.

    Examples
    --------

    .. code-block:: python

        from shiny import run_app

        # Run ``app`` inside ``./app.py``
        run_app()

        # Run ``app`` inside ``./myapp.py`` (or ``./myapp/app.py``)
        run_app("myapp")

        # Run ``my_app`` inside ``./myapp.py`` (or ``./myapp/app.py``)
        run_app("myapp:my_app")

        # Run ``my_app`` inside ``../myapp.py`` (or ``../myapp/app.py``)
        run_app("myapp:my_app", app_dir="..")
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
        # DON'T pass app_dir, we've already handled it ourselves
        # app_dir=app_dir,
    )


def resolve_app(app: str, app_dir: Optional[str]) -> str:
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
        if path.endswith(".py"):
            path = path[:-3]
        module = path.replace("/", ".").replace("\\", ".")
        instance = try_import_module(module)
        if not instance:
            raise ImportError(f"Could not find the module '{module}'")

    return f"{module}:{attr}"


def try_import_module(module: str) -> Optional[types.ModuleType]:
    try:
        if not importlib.util.find_spec(module):
            return None
    except ModuleNotFoundError:
        # find_spec throws this when the module contains both '/' and '.' characters
        return None
    except ImportError:
        # find_spec throws this when the module starts with "."
        return None

    # It's important for ModuleNotFoundError and ImportError (and any other error) NOT
    # to be caught here, as we want to report the true error to the user. Otherwise,
    # missing dependencies can be misreported to the user as the app module itself not
    # being found.
    return importlib.import_module(module)
