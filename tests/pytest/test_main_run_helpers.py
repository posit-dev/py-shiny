"""Tests for shiny._main helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from shiny import _main


def test_resolve_app_from_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text("x")

    result, app_dir = _main.resolve_app(str(app_file), None)
    assert result.endswith(":app")
    assert app_dir == str(tmp_path)

    with pytest.raises(SystemExit):
        _main.resolve_app("missing.py", str(tmp_path))


def test_try_import_module_handles_missing() -> None:
    assert _main.try_import_module("nonexistent.module") is None


def test_setup_hot_reload_and_launch_browser() -> None:
    log_config: dict[str, dict[str, dict[str, object]]] = {
        "handlers": {},
        "loggers": {"uvicorn.error": {}},
    }
    _main.setup_hot_reload(log_config, 1, 2, False)
    assert "shiny_hot_reload" in log_config["handlers"]

    log_config = {"handlers": {}, "loggers": {"uvicorn.error": {}}}
    _main.setup_launch_browser(log_config)
    assert "shiny_launch_browser" in log_config["handlers"]


def test_set_workbench_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_main, "is_workbench", lambda: True)
    kwargs = {"ws_per_message_deflate": True}
    _main._set_workbench_kwargs(kwargs)
    assert kwargs["ws_per_message_deflate"] is False


def test_run_app_uses_uvicorn(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called = {}

    def fake_run(*args: object, **kwargs: object) -> None:
        called["args"] = args
        called["kwargs"] = kwargs

    monkeypatch.setattr("uvicorn.run", fake_run)

    def fake_is_express_app(*_: object) -> bool:
        return False

    def fake_resolve_app(app: str, app_dir: str | None) -> tuple[str, str]:
        return ("app:app", str(tmp_path))

    monkeypatch.setattr("shiny._main.is_express_app", fake_is_express_app)
    monkeypatch.setattr("shiny._main.resolve_app", fake_resolve_app)

    _main.run_app("app.py:app", port=1234, reload=False)

    assert called["kwargs"]["port"] == 1234
