from __future__ import annotations

import copy
import importlib
import importlib.util
import inspect
import os
import platform
import re
import sys
import types
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, Optional

import click
import uvicorn.config

import shiny

from .. import _autoreload, _launchbrowser, _utils
from .._docstring import no_example
from .._uvicorn import (
    ReloadArgs,
    _run_uvicorn,
    _set_workbench_kwargs,
    maybe_setup_rsw_proxying,
)
from ..bookmark._bookmark_state import shiny_bookmarks_folder_name
from ..express import is_express_app
from ..express._utils import escape_to_var_name

stop_shortcut = "Ctrl+C"

RELOAD_INCLUDES_DEFAULT = (
    "*.py",
    "*.css",
    "*.scss",
    "*.js",
    "*.htm",
    "*.html",
    "*.png",
    "*.yml",
    "*.yaml",
)
RELOAD_EXCLUDES_DEFAULT = (
    ".*",
    "*.py[cod]",
    "__pycache__",
    "env",
    "venv",
    ".venv",
    shiny_bookmarks_folder_name,
)


@click.command(
    "run",
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
""",
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
    help="Enable auto-reload. See --reload-includes for types of files that are monitored for changes.",
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
    "--reload-includes",
    "reload_includes",
    default=",".join(RELOAD_INCLUDES_DEFAULT),
    help="File glob(s) to indicate which files should be monitored for changes. Defaults"
    f' to "{",".join(RELOAD_INCLUDES_DEFAULT)}".',
)
@click.option(
    "--reload-excludes",
    "reload_excludes",
    default=",".join(RELOAD_EXCLUDES_DEFAULT),
    help="File glob(s) to indicate which files should be excluded from file monitoring. Defaults"
    f' to "{",".join(RELOAD_EXCLUDES_DEFAULT)}".',
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
@click.option(
    "--dev-mode/--no-dev-mode",
    is_flag=True,
    default=True,
    help="Dev mode",
    show_default=True,
)
@no_example()
def run(
    app: str | shiny.App,
    host: str,
    port: int,
    *,
    autoreload_port: int,
    reload: bool,
    reload_dirs: tuple[str, ...],
    reload_includes: str,
    reload_excludes: str,
    ws_max_size: int,
    log_level: str,
    app_dir: str,
    factory: bool,
    launch_browser: bool,
    dev_mode: bool,
    **kwargs: object,
) -> None:
    reload_includes_list = reload_includes.split(",")
    reload_excludes_list = reload_excludes.split(",")
    return run_app(
        app,
        host=host,
        port=port,
        autoreload_port=autoreload_port,
        reload=reload,
        reload_dirs=list(reload_dirs),
        reload_includes=reload_includes_list,
        reload_excludes=reload_excludes_list,
        ws_max_size=ws_max_size,
        log_level=log_level,
        app_dir=app_dir,
        factory=factory,
        launch_browser=launch_browser,
        dev_mode=dev_mode,
        **kwargs,
    )


def run_app(
    app: str | shiny.App = "app:app",
    host: str = "127.0.0.1",
    port: int = 8000,
    *,
    autoreload_port: int = 0,
    reload: bool = False,
    reload_dirs: Optional[list[str]] = None,
    reload_includes: list[str] | tuple[str, ...] = RELOAD_INCLUDES_DEFAULT,
    reload_excludes: list[str] | tuple[str, ...] = RELOAD_EXCLUDES_DEFAULT,
    ws_max_size: int = 16777216,
    log_level: Optional[str] = None,
    app_dir: Optional[str] = ".",
    factory: bool = False,
    launch_browser: bool = False,
    dev_mode: bool = True,
    **kwargs: object,
) -> None:
    """
    Starts a Shiny app. Press ``Ctrl+C`` (or ``Ctrl+Break`` on Windows) to stop the app.

    Parameters
    ----------
    app
        The app to run. The default, ``app:app``, represents the "usual" case where the
        application is named ``app`` inside a ``app.py`` file within the current working
        directory. In other cases, the app location can be specified as a
        ``<module>:<attribute>`` string where the ``:<attribute>`` is only necessary if
        the application is named something other than ``app``. Note that ``<module>``
        can be a relative path to a ``.py`` file or a directory (with an ``app.py`` file
        inside of it); and in this case, the relative path is resolved relative to the
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
    reload_dirs
        A list of directories (in addition to the app directory) to watch for changes that
        will trigger an app reload.
    reload_includes
        List or tuple of file globs to indicate which files should be monitored for
        changes. Can be combined with `reload_excludes`.
    reload_excludes
        List or tuple of file globs to indicate which files should be excluded from
        reload monitoring. Can be combined with `reload_includes`
    ws_max_size
        WebSocket max size message in bytes.
    log_level
        Log level.
    app_dir
        The directory to look for ``app`` under (by adding this to the ``PYTHONPATH``).
    factory
        Treat ``app`` as an application factory, i.e. a () -> <ASGI app> callable.
    launch_browser
        Launch app browser after app starts, using the Python webbrowser module.
    **kwargs
        Additional keyword arguments which are passed to ``uvicorn.run``. For more
        information see [Uvicorn documentation](https://www.uvicorn.org/).

    Tip
    ---
    The ``shiny run`` command-line interface (which comes installed with Shiny) provides
    the same functionality as `shiny.run_app()`.

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

    if dev_mode:
        os.environ["SHINY_DEV_MODE"] = "1"

    if isinstance(app, str):
        # Remove ":app" suffix if present. Normally users would just pass in the
        # filename without the trailing ":app", as in `shiny run app.py`, but the
        # default value for `shiny run` is "app.py:app", so we need to handle it.
        app_no_suffix = re.sub(r":app$", "", app)
        if is_express_app(app_no_suffix, app_dir):
            app_path = Path(app_no_suffix).resolve()
            # If the file is "/path/to/app.py", our entrypoint with the escaped filename
            # is "shiny.express.app:_2f_path_2f_to_2f_app_2e_py".
            app = "shiny.express.app:" + escape_to_var_name(str(app_path))
            app_dir = str(app_path.parent)

            # Express apps need min version of rsconnect-python to deploy correctly.
            _verify_rsconnect_version()
        else:
            app, app_dir = resolve_app(app, app_dir)

    if app_dir:
        app_dir = os.path.realpath(app_dir)

    log_config: dict[str, Any] = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)

    if reload_dirs is None:
        reload_dirs = []
        if app_dir is not None:
            reload_dirs = [app_dir]

    on_started: Callable[[], None] | None = None

    if reload:
        # Always watch the app_dir
        if app_dir and app_dir not in reload_dirs:
            reload_dirs.append(app_dir)
        # For developers of Shiny itself; autoreload the app when Shiny package changes
        if os.getenv("SHINY_PKG_AUTORELOAD"):
            shinypath = Path(inspect.getfile(shiny)).parent
            reload_dirs.append(str(shinypath))

        if autoreload_port == 0:
            autoreload_port = _utils.random_port(host=host)

        if autoreload_port == port:
            print(
                "Autoreload port is already being used by the app; disabling autoreload\n",
                file=sys.stderr,
            )
            reload = False
        else:
            _autoreload.start_server(
                autoreload_port, app_port=port, launch_browser=launch_browser
            )
            # In reload mode, on_started fires in a fresh worker process on every
            # restart, so it cannot remember whether the browser was already opened.
            # reload_end pings the long-lived autoreload server, which both launches
            # the browser once (when launch_browser is set) and broadcasts the page
            # refresh on later restarts. See nudge() in _autoreload.py.
            assert on_started is None
            on_started = _autoreload.reload_end

    reload_args: ReloadArgs = {}
    if reload:
        if shiny_bookmarks_folder_name in reload_excludes:
            # Related: https://github.com/posit-dev/py-shiny/pull/1950
            #
            # Temp hack to work around uvicorn
            # https://github.com/encode/uvicorn/pull/2602 which will incorrectly reload
            # an app if any matching files in `RELOAD_INCLUDES_DEFAULT` (e.g. `*.png`)
            # are uploaded within `shiny_bookmarks` (an excluded relative directory).
            #
            # By extending `reload_excludes` to ignore everything under the bookmarks folder, we
            # can prevent the unexpected reload from happening for the root session. File
            # matches are performed via `pathlib.PurePath.match`, which is a right-match and
            # only supports `*` glob.
            #
            # Ignore up to five modules deep. This should cover most cases.
            #
            # Note: file uploads are always in the root session, so they are always
            # stored in the root bookmark dir of `shiny_bookmarks_folder_name / *`.
            reload_excludes = [
                *reload_excludes,
                str(Path(shiny_bookmarks_folder_name) / "*"),
                str(Path(shiny_bookmarks_folder_name) / "*" / "*"),
                str(Path(shiny_bookmarks_folder_name) / "*" / "*" / "*"),
                str(Path(shiny_bookmarks_folder_name) / "*" / "*" / "*" / "*"),
                str(Path(shiny_bookmarks_folder_name) / "*" / "*" / "*" / "*" / "*"),
            ]

        reload_args = {
            "reload": reload,
            # Adding `reload_includes` param while `reload=False` produces an warning
            # https://github.com/encode/uvicorn/blob/d43afed1cfa018a85c83094da8a2dd29f656d676/uvicorn/config.py#L298-L304
            "reload_includes": list(reload_includes),
            "reload_excludes": list(reload_excludes),
            "reload_dirs": reload_dirs,
        }

    # Launch the browser directly only when the autoreload server isn't already
    # responsible for it (see the reload branch above). This check must stay after
    # that branch: on an autoreload port conflict it sets reload = False without
    # assigning on_started, and this fallback then handles --launch-browser.
    if launch_browser and not reload:
        assert on_started is None
        on_started = partial(_launchbrowser.launch_browser, host, port)

    maybe_setup_rsw_proxying(log_config)

    _set_workbench_kwargs(kwargs)

    _run_uvicorn(
        app,
        host=host,
        port=port,
        ws_max_size=ws_max_size,
        log_level=log_level,
        log_config=log_config,
        app_dir=app_dir,
        on_started=on_started,
        factory=factory,
        lifespan="on",
        # Don't allow shiny to use uvloop!
        # https://github.com/posit-dev/py-shiny/issues/1373
        loop="asyncio",
        **reload_args,  # pyright: ignore[reportArgumentType]
        **kwargs,
    )


def is_file(app: str) -> bool:
    return "/" in app or app.endswith(".py")


def resolve_app(app: str, app_dir: str | None) -> tuple[str, str | None]:
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
            print(f"Error: {module_path} not found\n", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(module_path):
            print(f"Error: {module_path} is not a file\n", file=sys.stderr)
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


# Check that the version of rsconnect supports Shiny Express; can be removed in the
# future once this version of rsconnect is widely used. The dependency on "packaging"
# can also be removed then, because it is only used here. (Added 2024-03)
def _verify_rsconnect_version() -> None:
    PACKAGE_NAME = "rsconnect-python"
    MIN_VERSION = "1.22.0"

    from importlib.metadata import PackageNotFoundError, version

    from packaging.version import parse

    try:
        installed_version = parse(version(PACKAGE_NAME))
        required_version = parse(MIN_VERSION)
        if installed_version < required_version:
            print(
                f"Warning: rsconnect-python {installed_version} is installed, but it does not support deploying Shiny Express applications. "
                f"Please upgrade to at least version {MIN_VERSION}. "
                "If you are using pip, you can run `pip install --upgrade rsconnect-python`",
                file=sys.stderr,
            )
    except PackageNotFoundError:
        pass
