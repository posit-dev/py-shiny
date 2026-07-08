from __future__ import annotations

import pytest
from click.testing import CliRunner

import shiny
from shiny._main import _static, main


def test_static_is_deprecated_and_exits_nonzero() -> None:
    result = CliRunner().invoke(main, ["static"])

    assert result.exit_code == 1
    assert "shinylive export" in result.output


def test_static_ignores_extra_args() -> None:
    # ignore_unknown_options/allow_extra_args let old invocations still reach
    # the deprecation message instead of a usage error
    result = CliRunner().invoke(main, ["static", "appdir", "destdir", "--flag"])

    assert result.exit_code == 1
    assert "shinylive export" in result.output


def test_static_assets_remove(monkeypatch: pytest.MonkeyPatch) -> None:
    removed: list[str] = []

    def fake_remove(shinylive_dir: str) -> None:
        removed.append(shinylive_dir)

    monkeypatch.setattr(_static, "get_default_shinylive_dir", lambda: "/fake/dir")
    monkeypatch.setattr(_static, "remove_shinylive_local", fake_remove)

    result = CliRunner().invoke(main, ["static-assets", "remove"])

    assert result.exit_code == 0
    assert "Removing /fake/dir" in result.output
    assert removed == ["/fake/dir"]


def test_static_assets_info(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(_static, "get_default_shinylive_dir", lambda: "/fake/dir")
    monkeypatch.setattr(
        _static, "print_shinylive_local_info", lambda: calls.append("info")
    )

    result = CliRunner().invoke(main, ["static-assets", "info"])

    assert result.exit_code == 0
    assert calls == ["info"]


def test_static_assets_unknown_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_static, "get_default_shinylive_dir", lambda: "/fake/dir")

    result = CliRunner().invoke(main, ["static-assets", "bogus"])

    assert result.exit_code != 0
    assert "Unknown command: bogus" in result.output


def test_static_assets_no_args_shows_help() -> None:
    result = CliRunner().invoke(main, ["static-assets"])

    # no_args_is_help exits 0 on older click versions and 2 on newer ones
    assert result.exit_code in (0, 2)
    assert "Usage:" in result.output


def test_cells_to_app(monkeypatch: pytest.MonkeyPatch) -> None:
    converted: list[tuple[str, str]] = []

    def fake_convert(json_file: str, py_file: str) -> None:
        converted.append((json_file, py_file))

    monkeypatch.setattr(shiny.quarto, "convert_code_cells_to_app_py", fake_convert)

    result = CliRunner().invoke(main, ["cells-to-app", "cells.json", "app.py"])

    assert result.exit_code == 0
    assert converted == [("cells.json", "app.py")]


def test_get_shiny_deps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shiny.quarto, "get_shiny_deps", lambda: '[{"name": "fake"}]')

    result = CliRunner().invoke(main, ["get-shiny-deps"])

    assert result.exit_code == 0
    assert result.output == '[{"name": "fake"}]\n'


def test_main_version() -> None:
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert shiny.__version__ in result.output
