from __future__ import annotations

import copy
import importlib
import importlib.util
import inspect
import os
import platform
import re
import shutil
import sys
import types
from pathlib import Path
from typing import Any, Optional

import click
import uvicorn
import uvicorn.config

import shiny

from . import _autoreload, _hostenv, _static, _utils
from ._typing_extensions import NotRequired, TypedDict


@click.group("main")
def main() -> None:
    pass


stop_shortcut = "Ctrl+C"


@main.command(
    help=f"""Run a Shiny app (press {stop_shortcut} to stop).

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
    "-h",
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port. If 0, a random port will be used.",
    show_default=True,
)
@click.option(
    "--autoreload-port",
    type=int,
    default=0,
    help="Bind autoreload socket to this port. If 0, a random port will be used. Ignored if --reload is not used.",
    show_default=True,
)
@click.option(
    "-r",
    "--reload",
    is_flag=True,
    default=False,
    help="Enable auto-reload, when these types of files change: .py .css .js .html",
)
@click.option(
    "--reload-dir",
    "reload_dirs",
    multiple=True,
    help="Indicate a directory `--reload` should (recursively) monitor for changes, in "
    "addition to the app's parent directory. Can be used more than once.",
    type=click.Path(exists=True),
)
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
    "-d",
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
@click.option(
    "-b",
    "--launch-browser",
    is_flag=True,
    default=False,
    help="Launch app browser after app starts, using the Python webbrowser module.",
    show_default=True,
)
def run(
    app: str | shiny.App,
    host: str,
    port: int,
    autoreload_port: int,
    reload: bool,
    reload_dirs: tuple[str, ...],
    ws_max_size: int,
    log_level: str,
    app_dir: str,
    factory: bool,
    launch_browser: bool,
) -> None:
    return run_app(
        app,
        host=host,
        port=port,
        autoreload_port=autoreload_port,
        reload=reload,
        reload_dirs=list(reload_dirs),
        ws_max_size=ws_max_size,
        log_level=log_level,
        app_dir=app_dir,
        factory=factory,
        launch_browser=launch_browser,
    )


def run_app(
    app: str | shiny.App = "app:app",
    host: str = "127.0.0.1",
    port: int = 8000,
    autoreload_port: int = 0,
    reload: bool = False,
    reload_dirs: Optional[list[str]] = None,
    ws_max_size: int = 16777216,
    log_level: Optional[str] = None,
    app_dir: Optional[str] = ".",
    factory: bool = False,
    launch_browser: bool = False,
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
        The port that the app should listen on. Set to 0 to use a random port.
    autoreload_port
        The port that should be used for an additional websocket that is used to support
        hot-reload. Set to 0 to use a random port.
    reload
        Enable auto-reload.
    ws_max_size
        WebSocket max size message in bytes.
    log_level
        Log level.
    app_dir
        Look for ``app`` under this directory (by adding this to the ``PYTHONPATH``).
    factory
        Treat ``app`` as an application factory, i.e. a () -> <ASGI app> callable.
    launch_browser
        Launch app browser after app starts, using the Python webbrowser module.

    Tip
    ---
    The ``shiny run`` command-line interface (which comes installed with Shiny) provides
    the same functionality as this function.

    Examples
    --------

    ```{python}
    #|eval: false
    from shiny import run_app

    # Run ``app`` inside ``./app.py``
    run_app()

    # Run ``app`` inside ``./myapp.py`` (or ``./myapp/app.py``)
    run_app("myapp")

    # Run ``my_app`` inside ``./myapp.py`` (or ``./myapp/app.py``)
    run_app("myapp:my_app")

    # Run ``my_app`` inside ``../myapp.py`` (or ``../myapp/app.py``)
    run_app("myapp:my_app", app_dir="..")
    ```
    """

    # If port is 0, randomize
    if port == 0:
        port = _utils.random_port(host=host)

    os.environ["SHINY_HOST"] = host
    os.environ["SHINY_PORT"] = str(port)

    if isinstance(app, str):
        app, app_dir = resolve_app(app, app_dir)

    if app_dir:
        app_dir = os.path.realpath(app_dir)

    log_config: dict[str, Any] = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)

    if reload_dirs is None:
        reload_dirs = []

    if reload:
        # Always watch the app_dir
        if app_dir:
            reload_dirs.append(app_dir)
        # For developers of Shiny itself; autoreload the app when Shiny package changes
        if os.getenv("SHINY_PKG_AUTORELOAD"):
            shinypath = Path(inspect.getfile(shiny)).parent
            reload_dirs.append(str(shinypath))

        if autoreload_port == 0:
            autoreload_port = _utils.random_port(host=host)

        if autoreload_port == port:
            sys.stderr.write(
                "Autoreload port is already being used by the app; disabling autoreload\n"
            )
            reload = False
        else:
            setup_hot_reload(log_config, autoreload_port, port, launch_browser)

    reload_args: ReloadArgs = {}
    if reload:
        reload_dirs = []
        if app_dir is not None:
            reload_dirs = [app_dir]

        reload_args = {
            "reload": reload,
            # Adding `reload_includes` param while `reload=False` produces an warning
            # https://github.com/encode/uvicorn/blob/d43afed1cfa018a85c83094da8a2dd29f656d676/uvicorn/config.py#L298-L304
            "reload_includes": ["*.py", "*.css", "*.js", "*.htm", "*.html", "*.png"],
            "reload_dirs": reload_dirs,
        }

    if launch_browser and not reload:
        setup_launch_browser(log_config)

    maybe_setup_rsw_proxying(log_config)

    uvicorn.run(  # pyright: ignore[reportUnknownMemberType]
        app,
        host=host,
        port=port,
        ws_max_size=ws_max_size,
        log_level=log_level,
        log_config=log_config,
        app_dir=app_dir,
        factory=factory,
        **reload_args,
    )


def setup_hot_reload(
    log_config: dict[str, Any],
    autoreload_port: int,
    app_port: int,
    launch_browser: bool,
) -> None:
    # The only way I've found to get notified when uvicorn decides to reload, is by
    # inserting a custom log handler.
    log_config["handlers"]["shiny_hot_reload"] = {
        "class": "shiny._autoreload.HotReloadHandler",
        "level": "INFO",
    }
    if "handlers" not in log_config["loggers"]["uvicorn.error"]:
        log_config["loggers"]["uvicorn.error"]["handlers"] = []
    log_config["loggers"]["uvicorn.error"]["handlers"].append("shiny_hot_reload")

    _autoreload.start_server(autoreload_port, app_port, launch_browser)


def setup_launch_browser(log_config: dict[str, Any]):
    log_config["handlers"]["shiny_launch_browser"] = {
        "class": "shiny._launchbrowser.LaunchBrowserHandler",
        "level": "INFO",
    }
    if "handlers" not in log_config["loggers"]["uvicorn.error"]:
        log_config["loggers"]["uvicorn.error"]["handlers"] = []
    log_config["loggers"]["uvicorn.error"]["handlers"].append("shiny_launch_browser")


def maybe_setup_rsw_proxying(log_config: dict[str, Any]) -> None:
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


def resolve_app(app: str, app_dir: Optional[str]) -> tuple[str, Optional[str]]:
    # The `app` parameter can be:
    #
    # - A module:attribute name
    # - An absolute or relative path to a:
    #   - .py file (look for app inside of it)
    #   - directory (look for app:app inside of it)
    # - A module name (look for :app) inside of it

    if platform.system() == "Windows" and re.match("^[a-zA-Z]:[/\\\\]", app):
        # On Windows, need special handling of ':' in some cases, like these:
        #   shiny run c:/Users/username/Documents/myapp/app.py
        #   shiny run c:\Users\username\Documents\myapp\app.py
        module, attr = app, ""
    else:
        module, _, attr = app.partition(":")
    if not module:
        raise ImportError("The APP parameter cannot start with ':'.")
    if not attr:
        attr = "app"

    if is_file(module):
        # Before checking module path, resolve it relative to app_dir if provided
        module_path = module if app_dir is None else os.path.join(app_dir, module)
        # TODO: We should probably be using some kind of loader
        # TODO: I don't like that we exit here, if we ever export this it would be bad;
        #       but also printing a massive stack trace for a `shiny run badpath` is way
        #       unfriendly. We should probably throw a custom error that the shiny run
        #       entrypoint knows not to print the stack trace for.
        if not os.path.exists(module_path):
            sys.stderr.write(f"Error: {module_path} not found\n")
            sys.exit(1)
        if not os.path.isfile(module_path):
            sys.stderr.write(f"Error: {module_path} is not a file\n")
            sys.exit(1)
        dirname, filename = os.path.split(module_path)
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
    help="""Create a Shiny application from a template.

APPDIR is the directory to the Shiny application. A file named app.py will be created in
that directory.

After creating the application, you use `shiny run`:

    shiny run APPDIR/app.py --reload
"""
)
@click.argument("appdir", type=str, default=".")
def create(appdir: str) -> None:
    app_dir = Path(appdir)
    app_path = app_dir / "app.py"
    if app_path.exists():
        print(f"Error: Can't create {app_path} because it already exists.")
        sys.exit(1)

    if not app_dir.exists():
        app_dir.mkdir()

    shutil.copyfile(
        Path(__file__).parent / "api-examples" / "template" / "app.py", app_path
    )

    print(f"Created Shiny app at {app_dir / 'app.py'}")


@main.command(
    help="""The functionality from `shiny static` has been moved to the shinylive package.
Please install shinylive and use `shinylive export` instead of `shiny static`:

  \b
  shiny static-assets remove
  pip install shinylive
  shinylive export APPDIR DESTDIR

""",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
def static() -> None:
    print(
        """The functionality from `shiny static` has been moved to the shinylive package.
Please install shinylive and use `shinylive export` instead of `shiny static`:

  shiny static-assets remove
  pip install shinylive
  shinylive export APPDIR DESTDIR
"""
    )
    sys.exit(1)


@main.command(
    no_args_is_help=True,
    help="""Manage local copy of assets for static app deployment. (Deprecated)

    \b
    Commands:
        remove: Remove local copies of assets.
        info: Print information about the local assets.

""",
)
@click.argument("command", type=str)
def static_assets(command: str) -> None:
    dir = _static.get_default_shinylive_dir()

    if command == "remove":
        print(f"Removing {dir}")
        _static.remove_shinylive_local(shinylive_dir=dir)
    elif command == "info":
        _static.print_shinylive_local_info()
    else:
        raise click.UsageError(f"Unknown command: {command}")


class ReloadArgs(TypedDict):
    reload: NotRequired[bool]
    reload_includes: NotRequired[list[str]]
    reload_dirs: NotRequired[list[str]]
