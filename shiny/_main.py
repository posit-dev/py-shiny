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
import warnings
from pathlib import Path
from typing import Any, Optional

import click
import uvicorn
import uvicorn.config

import shiny

from . import __version__, _autoreload, _hostenv, _static, _utils
from ._docstring import no_example
from ._hostenv import is_workbench
from ._typing_extensions import NotRequired, TypedDict
from .bookmark._bookmark_state import shiny_bookmarks_folder_name
from .express import is_express_app
from .express._utils import escape_to_var_name


@click.group("main")
@click.version_option(__version__)
def main() -> None:
    pass


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

    os.environ["SHINY_BROWSER_HOST"] = host
    os.environ["SHINY_BROWSER_PORT"] = str(port)
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
            setup_hot_reload(log_config, autoreload_port, port, launch_browser)

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

    if launch_browser and not reload:
        setup_launch_browser(log_config)

    maybe_setup_rsw_proxying(log_config)

    _set_workbench_kwargs(kwargs)

    uvicorn.run(  # pyright: ignore[reportUnknownMemberType]
        app,
        host=host,
        port=port,
        ws_max_size=ws_max_size,
        log_level=log_level,
        log_config=log_config,
        app_dir=app_dir,
        factory=factory,
        lifespan="on",
        # Don't allow shiny to use uvloop!
        # https://github.com/posit-dev/py-shiny/issues/1373
        loop="asyncio",
        **reload_args,  # pyright: ignore[reportArgumentType]
        **kwargs,
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


@main.group(help="""Add files to enhance your Shiny app.""")
def add() -> None:
    pass


@add.command(
    help="""Add a test file for a specified Shiny app.

Generate a comprehensive test file for a specified app using AI. The generator
will analyze your app code and create appropriate test cases with assertions.

After creating the test file, you can use `pytest` to run the tests:

        pytest TEST_FILE
"""
)
@click.option(
    "--app",
    "-a",
    type=str,
    help="Path to the app file for which you want to generate a test file.",
)
@click.option(
    "--test-file",
    "-t",
    type=str,
    help="Path for the generated test file. If not provided, will be auto-generated.",
)
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai"]),
    default="anthropic",
    help="AI provider to use for test generation.",
)
@click.option(
    "--model",
    type=str,
    help="Specific model to use (optional). Examples: haiku3.5, sonnet,  gpt-5, gpt-5-mini",
)
# Param for app.py, param for test_name
def test(
    app: str | None,
    test_file: str | None,
    provider: str,
    model: str | None,
) -> None:
    from ._main_generate_test import generate_test_file

    generate_test_file(
        app_file=app, output_file=test_file, provider=provider, model=model
    )


@main.command(
    help="""Create a Shiny application from a template.

Create an app based on a template. You will be prompted with
a number of application types, as well as the destination folder.
If you don't provide a destination folder, it will be created in the current working
directory based on the template name.

After creating the application, you use `shiny run`:

    shiny run APPDIR/app.py --reload
"""
)
@click.option(
    "--template",
    "-t",
    type=click.STRING,
    help="Choose a template for your new application.",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(
        ["core", "express"],
        case_sensitive=False,
    ),
    help="Do you want to use a Shiny Express template or a Shiny Core template?",
)
@click.option(
    "--github",
    "-g",
    help="""
    The GitHub repo containing the template, e.g. 'posit-dev/py-shiny-templates'.
    Can be in the format '{repo_owner}/{repo_name}', '{repo_owner}/{repo_name}@{ref}',
    or '{repo_owner}/{repo_name}:{path}@{ref}'.
    Alternatively, a GitHub URL of the template sub-directory, e.g
    'https://github.com/posit-dev/py-shiny-templates/tree/main/dashboard'.
    """,
)
@click.option(
    "--dir",
    "-d",
    type=str,
    help="The destination directory, you will be prompted if this is not provided.",
)
@click.option(
    "--package-name",
    help="""
    If you are using one of the JavaScript component templates,
    you can use this flag to specify the name of the resulting package without being prompted.
    """,
)
def create(
    template: Optional[str] = None,
    mode: Optional[str] = None,
    github: Optional[str] = None,
    dir: Optional[Path | str] = None,
    package_name: Optional[str] = None,
) -> None:
    from ._main_create import use_github_template, use_internal_template

    if dir is not None:
        dir = Path(dir)

    if github is not None:
        use_github_template(
            github,
            template_name=template,
            mode=mode,
            dest_dir=dir,
            package_name=package_name,
        )
    else:
        use_internal_template(template, mode, dir, package_name)


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


@main.command(help="""Convert a JSON file with code cells to a py file.""")
@click.argument(
    "json_file",
    type=str,
)
@click.argument(
    "py_file",
    type=str,
)
def cells_to_app(json_file: str, py_file: str) -> None:
    shiny.quarto.convert_code_cells_to_app_py(json_file, py_file)


@main.command(help="""Get Shiny's HTML dependencies as JSON.""")
def get_shiny_deps() -> None:
    print(shiny.quarto.get_shiny_deps())


class ReloadArgs(TypedDict):
    reload: NotRequired[bool]
    reload_includes: NotRequired[list[str]]
    reload_excludes: NotRequired[list[str]]
    reload_dirs: NotRequired[list[str]]


def _set_workbench_kwargs(kwargs: dict[str, Any]) -> None:
    if is_workbench():
        if kwargs.get("ws_per_message_deflate"):
            # Workaround for nginx/uvicorn issue within Workbench
            # https://github.com/rstudio/rstudio-pro/issues/7368#issuecomment-2918016088
            warnings.warn(
                "Overwriting kwarg `ws_per_message_deflate=True` to `False` to avoid breaking issue in Workbench",
                stacklevel=2,
            )
        kwargs["ws_per_message_deflate"] = False


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
