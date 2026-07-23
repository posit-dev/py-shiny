from __future__ import annotations

import inspect
import logging
import os
import socket
import sys
import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from uvicorn.config import Config
from uvicorn.server import Server
from uvicorn.supervisors import ChangeReload, Multiprocess

if TYPE_CHECKING:
    # Type-only import: uvicorn._types is a private module, so don't depend
    # on it at runtime.
    from uvicorn._types import ASGIApplication

from ._hostenv import is_workbench
from ._typing_extensions import NotRequired, TypedDict

# Mirrors uvicorn's STARTUP_FAILURE exit code, which is only importable
# (from uvicorn.config) in uvicorn >= 0.50, and we support >= 0.23.
_UVICORN_STARTUP_FAILURE = 3


class ShinyConfig(Config):
    # uvicorn's Config assigns these in __init__, but the generated stubs
    # (`make pyright-typings`) omit instance attributes, so declare them here.
    reload: bool
    workers: int
    uds: str | None


class ShinyServer(Server):
    # uvicorn's Server assigns this in __init__; see ShinyConfig note above.
    started: bool

    # In reload mode, on_started travels with the server target, so keep it picklable.
    def __init__(
        self, config: Config, on_started: Callable[[], None] | None = None
    ) -> None:
        super().__init__(config=config)
        self._on_started = on_started

    async def startup(self, sockets: list[socket.socket] | None = None) -> None:
        await super().startup(sockets=sockets)
        if self.started and self._on_started is not None:
            self._on_started()


def _run_uvicorn(
    app: ASGIApplication | Callable[..., Any] | str,
    *,
    app_dir: str | None = None,
    on_started: Callable[[], None] | None = None,
    **kwargs: Any,
) -> None:
    # Mirrors uvicorn.run(); re-check this helper when upgrading Uvicorn.
    if app_dir is not None:
        sys.path.insert(0, app_dir)

    config = ShinyConfig(app, **kwargs)
    server = ShinyServer(config=config, on_started=on_started)

    if config.reload or config.workers > 1:
        if not isinstance(app, str):
            logging.getLogger("uvicorn.error").warning(
                "You must pass the application as an import string to enable "
                "'reload' or 'workers'."
            )
            sys.exit(_UVICORN_STARTUP_FAILURE)
    else:
        # Fail fast on app import errors before binding the socket, matching
        # uvicorn.run(). Config.load_app() only exists in uvicorn >= 0.47;
        # older supported versions (>= 0.23) load the app inside serve() instead.
        load_app = getattr(config, "load_app", None)
        if load_app is not None:
            load_app()

    try:
        if config.should_reload:
            sock = config.bind_socket()
            ChangeReload(config, target=server.run, sockets=[sock]).run()
        elif config.workers > 1:
            sock = config.bind_socket()
            # uvicorn 0.51.0 removed Multiprocess's target parameter: each worker
            # now builds its own Server from config, so on_started does not fire
            # in multi-worker mode there. Older supported versions require the
            # target. Only one spelling can match the generated stubs at a time,
            # hence the pyright ignores on both.
            if "target" in inspect.signature(Multiprocess.__init__).parameters:
                Multiprocess(
                    config,
                    target=server.run,  # pyright: ignore[reportCallIssue]
                    sockets=[sock],
                ).run()
            else:
                Multiprocess(
                    config, sockets=[sock]
                ).run()  # pyright: ignore[reportCallIssue]
        else:
            server.run()
    except KeyboardInterrupt:
        pass
    finally:
        uds = config.uds
        if uds and os.path.exists(uds):
            os.remove(uds)

    if not server.started and not config.should_reload and config.workers == 1:
        sys.exit(_UVICORN_STARTUP_FAILURE)


def maybe_setup_rsw_proxying(log_config: dict[str, Any]) -> None:
    # Replace localhost URLs emitted to the log, with proxied URLs
    if is_workbench():
        if "filters" not in log_config:
            log_config["filters"] = {}
        log_config["filters"]["rsw_proxy"] = {"()": "shiny._hostenv.ProxyUrlFilter"}
        if "filters" not in log_config["handlers"]["default"]:
            log_config["handlers"]["default"]["filters"] = []
        log_config["handlers"]["default"]["filters"].append("rsw_proxy")


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
