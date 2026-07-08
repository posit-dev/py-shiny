import asyncio
import logging
import warnings
from typing import Any, Dict, cast

import pytest
from uvicorn.config import Config
from uvicorn.server import Server

from shiny import _main_run
from shiny._uvicorn import ShinyServer, _set_workbench_kwargs


def test_shiny_server_calls_on_started(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []

    async def startup(self: Server, sockets: list[Any] | None = None) -> None:
        cast(Any, self).started = True

    monkeypatch.setattr(Server, "startup", startup)

    server = ShinyServer(
        config=Config("app:app"), on_started=lambda: calls.append("started")
    )
    asyncio.run(server.startup())

    assert calls == ["started"]


def test_launch_browser_callback_ignores_log_level(monkeypatch: pytest.MonkeyPatch):
    captured_kwargs: dict[str, Any] = {}
    browser_calls: list[tuple[str, int]] = []

    def run_uvicorn(app: Any, **kwargs: Any) -> None:
        captured_kwargs.update(kwargs)

    monkeypatch.setattr(_main_run, "_run_uvicorn", run_uvicorn)

    def launch_browser(host: str, port: int) -> None:
        browser_calls.append((host, port))

    monkeypatch.setattr(_main_run._launchbrowser, "launch_browser", launch_browser)

    _main_run.run_app(
        cast(Any, object()),
        host="127.0.0.1",
        port=8765,
        log_level="warning",
        launch_browser=True,
        # Keep run_app() from setting SHINY_DEV_MODE=1 in the pytest process.
        dev_mode=False,
    )

    logging.disable(logging.INFO)
    try:
        captured_kwargs["on_started"]()
    finally:
        logging.disable(logging.NOTSET)

    assert captured_kwargs["log_level"] == "warning"
    assert browser_calls == [("127.0.0.1", 8765)]


def test_reload_uses_startup_callback_not_log_handler(monkeypatch: pytest.MonkeyPatch):
    captured_kwargs: dict[str, Any] = {}
    reload_calls: list[str] = []
    start_server_calls: list[tuple[int, int, bool]] = []

    def run_uvicorn(app: Any, **kwargs: Any) -> None:
        captured_kwargs.update(kwargs)

    monkeypatch.setattr(_main_run, "_run_uvicorn", run_uvicorn)
    monkeypatch.setattr(
        _main_run._autoreload, "reload_end", lambda: reload_calls.append("reload_end")
    )

    def start_server(autoreload_port: int, app_port: int, launch_browser: bool) -> None:
        start_server_calls.append((autoreload_port, app_port, launch_browser))

    monkeypatch.setattr(_main_run._autoreload, "start_server", start_server)

    _main_run.run_app(
        cast(Any, object()),
        port=8765,
        autoreload_port=8766,
        reload=True,
        launch_browser=True,
        reload_dirs=[],
        log_level="warning",
        # Keep run_app() from setting SHINY_DEV_MODE=1 in the pytest process.
        dev_mode=False,
    )

    captured_kwargs["on_started"]()

    log_config = captured_kwargs["log_config"]
    assert "shiny_hot_reload" not in log_config["handlers"]
    assert "shiny_hot_reload" not in log_config["loggers"]["uvicorn.error"].get(
        "handlers", []
    )
    assert start_server_calls == [(8766, 8765, True)]
    assert reload_calls == ["reload_end"]


def test_workbench_kwargs_if_url_set(monkeypatch: pytest.MonkeyPatch):
    """
    Test that the `ws_per_message_deflate` kwarg is set to False when
    RS_SERVER_URL and RS_SESSION_URL are set in the environment.
    This is to avoid breaking issues in Workbench.
    If the kwargs are set to True, a warning is raised and the value is set to False.
    """
    # Workbench URL is set, kwargs are not
    monkeypatch.setenv("RS_SERVER_URL", "any_string")
    monkeypatch.setenv("RS_SESSION_URL", "any_string")

    kwargs: Dict[str, Any] = {}
    _set_workbench_kwargs(kwargs)
    assert kwargs.get("ws_per_message_deflate") is False

    # kwarg have been set to True
    kwargs = {
        "ws_per_message_deflate": True,
    }
    with pytest.warns(UserWarning):
        warnings.warn(
            "Overwriting kwarg `ws_per_message_deflate=True` to `False` to avoid breaking issue in Workbench",
            UserWarning,
            stacklevel=2,
        )
        _set_workbench_kwargs(kwargs)
        assert kwargs.get("ws_per_message_deflate") is False


def test_workbench_kwargs_if_url_not_set():
    """
    Test that the `ws_per_message_deflate` kwarg is not changed if the RS_SERVER_URL and RS_SESSION_URL environment variables are not set.
    """
    kwargs: Dict[str, Any] = {
        "ws_per_message_deflate": True,
    }
    _set_workbench_kwargs(kwargs)
    assert kwargs.get("ws_per_message_deflate") is True

    kwargs: Dict[str, Any] = {}
    _set_workbench_kwargs(kwargs)
    assert kwargs.get("ws_per_message_deflate") is None
