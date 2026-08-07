from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from shiny._main import _run, main
from shiny.express._utils import escape_to_var_name


@pytest.fixture
def captured_run_app(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Replace run_app with a recorder so `shiny run` never starts a server."""
    captured: dict[str, Any] = {}

    def fake_run_app(app: Any, **kwargs: Any) -> None:
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr(_run, "run_app", fake_run_app)
    return captured


@pytest.fixture
def captured_uvicorn(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Replace _run_uvicorn with a recorder so `run_app` never starts a server."""
    captured: dict[str, Any] = {}

    def fake_run_uvicorn(app: Any, **kwargs: Any) -> None:
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr(_run, "_run_uvicorn", fake_run_uvicorn)
    return captured


def test_run_defaults(captured_run_app: dict[str, Any]) -> None:
    result = CliRunner().invoke(main, ["run"])

    assert result.exit_code == 0
    assert captured_run_app["app"] == "app.py:app"
    assert captured_run_app["host"] == "127.0.0.1"
    assert captured_run_app["port"] == 8000
    assert captured_run_app["reload"] is False
    assert captured_run_app["reload_includes"] == list(_run.RELOAD_INCLUDES_DEFAULT)
    assert captured_run_app["reload_excludes"] == list(_run.RELOAD_EXCLUDES_DEFAULT)
    assert captured_run_app["launch_browser"] is False
    assert captured_run_app["dev_mode"] is True


def test_run_options_are_forwarded(
    captured_run_app: dict[str, Any], tmp_path: Path
) -> None:
    result = CliRunner().invoke(
        main,
        [
            "run",
            "myapp.py:my_app",
            "--host",
            "0.0.0.0",
            "--port",
            "4242",
            "--reload",
            "--reload-dir",
            str(tmp_path),
            "--reload-includes",
            "*.py,*.txt",
            "--reload-excludes",
            ".*,node_modules",
            "--app-dir",
            "some/dir",
            "--factory",
            "--launch-browser",
            "--no-dev-mode",
        ],
    )

    assert result.exit_code == 0
    assert captured_run_app["app"] == "myapp.py:my_app"
    assert captured_run_app["host"] == "0.0.0.0"
    assert captured_run_app["port"] == 4242
    assert captured_run_app["reload"] is True
    assert captured_run_app["reload_dirs"] == [str(tmp_path)]
    # Comma-separated globs are split into lists
    assert captured_run_app["reload_includes"] == ["*.py", "*.txt"]
    assert captured_run_app["reload_excludes"] == [".*", "node_modules"]
    assert captured_run_app["app_dir"] == "some/dir"
    assert captured_run_app["factory"] is True
    assert captured_run_app["launch_browser"] is True
    assert captured_run_app["dev_mode"] is False


def test_run_rejects_missing_reload_dir(captured_run_app: dict[str, Any]) -> None:
    result = CliRunner().invoke(
        main, ["run", "--reload-dir", "does/not/exist/anywhere"]
    )

    assert result.exit_code != 0
    assert captured_run_app == {}


def test_is_file() -> None:
    assert _run.is_file("app.py")
    assert _run.is_file("some/dir/app")
    assert not _run.is_file("app")
    assert not _run.is_file("mymodule")


def test_resolve_app_module_and_attr_passthrough() -> None:
    assert _run.resolve_app("mymod:my_app", "/x") == ("mymod:my_app", "/x")


def test_resolve_app_default_attr() -> None:
    assert _run.resolve_app("mymod", None) == ("mymod:app", None)


def test_resolve_app_from_file(tmp_path: Path) -> None:
    (tmp_path / "myapp.py").write_text("app = None\n")

    assert _run.resolve_app(str(tmp_path / "myapp.py"), None) == (
        "myapp:app",
        str(tmp_path),
    )


def test_resolve_app_file_relative_to_app_dir(tmp_path: Path) -> None:
    (tmp_path / "myapp.py").write_text("app = None\n")

    assert _run.resolve_app("myapp.py", str(tmp_path)) == (
        "myapp:app",
        str(tmp_path),
    )


def test_resolve_app_missing_file_exits(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        _run.resolve_app(str(tmp_path / "nope.py"), None)


def test_resolve_app_directory_exits(tmp_path: Path) -> None:
    # A path that exists but is not a file
    with pytest.raises(SystemExit):
        _run.resolve_app(str(tmp_path) + "/", None)


def test_resolve_app_empty_module_raises() -> None:
    with pytest.raises(ImportError):
        _run.resolve_app(":app", None)


def write_express_app(app_dir: Path, filename: str = "app.py") -> Path:
    app_dir.mkdir(parents=True, exist_ok=True)
    app_file = app_dir / filename
    app_file.write_text("from shiny.express import ui\n\nui.h1('hello')\n")
    return app_file


def express_entrypoint(app_file: Path) -> str:
    return "shiny.express.app:" + escape_to_var_name(str(app_file.resolve()))


def test_run_app_express_resolves_relative_to_app_dir(
    captured_uvicorn: dict[str, Any], tmp_path: Path
) -> None:
    # https://github.com/posit-dev/py-shiny/issues/1991
    app_file = write_express_app(tmp_path / "subdir")

    _run.run_app("app.py", app_dir=str(tmp_path / "subdir"), dev_mode=False)

    assert captured_uvicorn["app"] == express_entrypoint(app_file)
    assert captured_uvicorn["app_dir"] == os.path.realpath(tmp_path / "subdir")


def test_run_app_express_relative_app_dir(
    captured_uvicorn: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The reported reproduction: `shiny run --app-dir subdir app.py`
    app_file = write_express_app(tmp_path / "subdir")
    monkeypatch.chdir(tmp_path)

    _run.run_app("app.py", app_dir="subdir", dev_mode=False)

    assert captured_uvicorn["app"] == express_entrypoint(app_file)
    assert captured_uvicorn["app_dir"] == os.path.realpath(tmp_path / "subdir")


def test_run_app_express_default_app_suffix_with_app_dir(
    captured_uvicorn: dict[str, Any], tmp_path: Path
) -> None:
    # `shiny run -d subdir` uses the default APP value of "app.py:app"
    app_file = write_express_app(tmp_path / "subdir")

    _run.run_app("app.py:app", app_dir=str(tmp_path / "subdir"), dev_mode=False)

    assert captured_uvicorn["app"] == express_entrypoint(app_file)
    assert captured_uvicorn["app_dir"] == os.path.realpath(tmp_path / "subdir")


def test_run_app_express_absolute_app_path_ignores_app_dir(
    captured_uvicorn: dict[str, Any], tmp_path: Path
) -> None:
    # An absolute APP path wins over app_dir (as documented for `--app-dir`)
    app_file = write_express_app(tmp_path / "subdir")

    _run.run_app(str(app_file), app_dir=str(tmp_path / "other"), dev_mode=False)

    assert captured_uvicorn["app"] == express_entrypoint(app_file)
    assert captured_uvicorn["app_dir"] == os.path.realpath(tmp_path / "subdir")


def test_run_app_express_no_app_dir(
    captured_uvicorn: dict[str, Any], tmp_path: Path
) -> None:
    app_file = write_express_app(tmp_path / "subdir")

    _run.run_app(str(app_file), app_dir=None, dev_mode=False)

    assert captured_uvicorn["app"] == express_entrypoint(app_file)
    assert captured_uvicorn["app_dir"] == os.path.realpath(tmp_path / "subdir")


def test_try_import_module() -> None:
    assert _run.try_import_module("os") is os
    assert _run.try_import_module("definitely_not_a_module_abc123") is None
    # '/' and '.' together make find_spec throw ModuleNotFoundError
    assert _run.try_import_module("foo/bar.baz") is None
    # Leading '.' makes find_spec throw ImportError
    assert _run.try_import_module(".relative") is None
