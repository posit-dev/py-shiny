import copy
import importlib
import importlib.util
import os
import re
import sys
import types
from typing import Optional, Union, Tuple, Any, Dict, cast

import click
import uvicorn
import uvicorn.config

import shiny
from . import _autoreload
from . import _hostenv
from ._static import deploy_static


@click.group()  # pyright: ignore[reportUnknownMemberType]
def main() -> None:
    pass


stop_shortcut = "Ctrl+C"


@main.command(
    help=f"""Runs a Shiny app. Press {stop_shortcut} to stop.

The APP argument indicates the Python file (or module) and attribute where the
shiny.App object can be found. For example, if the current directory contains
a file called app.py, which contains an `app` variable that is the Shiny app,
any of the following will work:

\b
  * shiny run             # app:app is assumed
  * shiny run app         # :app is assumed
  * shiny run app.py      # :app is assumed
  * shiny run app:app
  * shiny run app.py:app
"""
)
@click.argument("app", default="app.py:app")
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
    "--autoreload-port",
    type=str,
    default="+123",
    help="Bind autoreload socket to this port number. If the value begins with + or -, it will be added to the value of --port. Ignored if --reload is not used.",
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
    " Defaults to the current working directory. If APP is a file path, this argument"
    " is ignored.",
)
@click.option(
    "--factory",
    is_flag=True,
    default=False,
    help="Treat APP as an application factory, i.e. a () -> <ASGI app> callable.",
    show_default=True,
)
def run(
    app: Union[str, shiny.App],
    host: str,
    port: int,
    autoreload_port: str,
    debug: bool,
    reload: bool,
    ws_max_size: int,
    log_level: str,
    app_dir: str,
    factory: bool,
) -> None:
    return run_app(
        app,
        host=host,
        port=port,
        autoreload_port=autoreload_port,
        debug=debug,
        reload=reload,
        ws_max_size=ws_max_size,
        log_level=log_level,
        app_dir=app_dir,
        factory=factory,
    )


def run_app(
    app: Union[str, shiny.App] = "app:app",
    host: str = "127.0.0.1",
    port: int = 8000,
    autoreload_port: str = "",
    debug: bool = False,
    reload: bool = False,
    ws_max_size: int = 16777216,
    log_level: Optional[str] = None,
    app_dir: Optional[str] = ".",
    factory: bool = False,
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
        app, app_dir = resolve_app(app, app_dir)

    if app_dir:
        app_dir = os.path.realpath(app_dir)

    log_config: Dict[str, Any] = copy.deepcopy(
        cast(
            Dict[str, Any],
            uvicorn.config.LOGGING_CONFIG,  # pyright: ignore[reportUnknownMemberType]
        )
    )

    if reload and autoreload_port != "":
        m = re.search("^([+-]?)(\\d+)$", autoreload_port)
        if not m:
            sys.stderr.write(
                "Error: Couldn't understand the provided value for --autoreload-port\n"
            )
            exit(1)
        autoreload_port_num = int(m.group(2))
        if m.group(1) == "+":
            autoreload_port_num += port
        elif m.group(1) == "-":
            autoreload_port_num = port - autoreload_port_num

        if autoreload_port_num == port:
            sys.stderr.write(
                "Autoreload port is already being used by the app; disabling autoreload\n"
            )
        else:
            setup_hot_reload(log_config, autoreload_port_num)

    maybe_setup_rsw_proxying(log_config)

    uvicorn.run(
        app,  # type: ignore
        host=host,
        port=port,
        debug=debug,
        reload=reload,
        reload_dirs=[app_dir] if reload else [],
        ws_max_size=ws_max_size,
        log_level=log_level,
        log_config=log_config,
        app_dir=app_dir,
        factory=factory,
    )


def setup_hot_reload(log_config: Dict[str, Any], port: int) -> None:
    # The only way I've found to get notified when uvicorn decides to reload, is by
    # inserting a custom log handler.
    log_config["handlers"]["shiny_hot_reload"] = {
        "class": "shiny._autoreload.HotReloadHandler",
        "level": "INFO",
    }
    log_config["loggers"]["uvicorn.error"]["handlers"] = ["shiny_hot_reload"]

    _autoreload.start_server(port)


def maybe_setup_rsw_proxying(log_config: Dict[str, Any]) -> None:
    # Replace localhost URLs emitted to the log, with proxied URLs
    if _hostenv.is_workbench():
        if "filters" not in log_config:
            log_config["filters"] = {}
        log_config["filters"]["rsw_proxy"] = {"()": "shiny._hostenv.ProxyUrlFilter"}
        if "filters" not in log_config["handlers"]["default"]:
            log_config["handlers"]["default"]["filters"] = []
        log_config["handlers"]["default"]["filters"].append("rsw_proxy")


def is_file(app: str) -> bool:
    return "/" in app or app.endswith(".py")


def resolve_app(app: str, app_dir: Optional[str]) -> Tuple[str, Optional[str]]:
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

    if is_file(module):
        # TODO: We should probably be using some kind of loader
        # TODO: I don't like that we exit here, if we ever export this it would be bad;
        #       but also printing a massive stack trace for a `shiny run badpath` is way
        #       unfriendly. We should probably throw a custom error that the shiny run
        #       entrypoint knows not to print the stack trace for.
        if not os.path.exists(module):
            sys.stderr.write(f"Error: {module} not found\n")
            sys.exit(1)
        if not os.path.isfile(module):
            sys.stderr.write(f"Error: {module} is not a file\n")
            sys.exit(1)
        dirname, filename = os.path.split(module)
        module = filename[:-3] if filename.endswith(".py") else filename
        app_dir = dirname

    return f"{module}:{attr}", app_dir


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


@main.command(
    help="""Create a statically deployable distribution for a Shiny app.

APPDIR is the directory containing the Shiny application.

DESTDIR is the destination directory where the output files will be written to. This
directory can be deployed as a static web site.

After writing the output files, you can serve them locally with the following command:

    python3 -m http.server --directory DESTDIR 8000
"""
)
@click.argument("appdir", type=str)
@click.argument("destdir", type=str)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing files in the destination directory.",
    show_default=True,
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Print debugging information when copying files.",
    show_default=True,
)
@click.option(
    "--subdir",
    type=str,
    default=None,
    help="Subdir in which to put the app.",
    show_default=True,
)
def static(
    appdir: str, destdir: str, overwrite: bool, subdir: str, verbose: bool
) -> None:

    deploy_static(appdir, destdir, overwrite=overwrite, subdir=subdir, verbose=verbose)
