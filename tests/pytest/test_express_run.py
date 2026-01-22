"""Tests for shiny.express._run helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from htmltools import Tag, TagList

from shiny.express import _run as express_run
from shiny.express._run import (
    InputNotImportedShim,
    _merge_app_opts,
    _normalize_app_opts,
    app_opts,
    create_express_app,
    run_express,
)
from shiny.express._stub_session import ExpressStubSession
from shiny.session import session_context


def _write_express_app(path: Path, body: str) -> None:
    path.write_text(
        "\n".join(
            [
                "from shiny.express import ui, app_opts",
                body,
            ]
        )
    )


def test_app_opts_requires_stub_session() -> None:
    with pytest.raises(RuntimeError, match="standalone Shiny Express app"):
        app_opts(debug=True)


def test_app_opts_ignores_non_stub_session(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySession:
        pass

    monkeypatch.setattr(express_run, "get_current_session", lambda: DummySession())
    app_opts(debug=True)


def test_app_opts_sets_values() -> None:
    stub = ExpressStubSession()
    with session_context(stub):
        app_opts(static_assets="assets", bookmark_store="url", debug=True)

    static_assets = stub.app_opts["static_assets"]
    assert static_assets["/"] == Path("assets")
    assert stub.app_opts["bookmark_store"] == "url"
    assert stub.app_opts["debug"] is True


def test_merge_and_normalize_app_opts(tmp_path: Path) -> None:
    base = {"static_assets": {"/": Path("www")}, "debug": False}
    updates = {"static_assets": {"/foo": Path("assets")}, "bookmark_store": "url"}

    merged = _merge_app_opts(base, updates)
    assert merged["static_assets"]["/foo"] == Path("assets")
    assert merged["bookmark_store"] == "url"

    normalized = _normalize_app_opts(merged, tmp_path)
    assert normalized["static_assets"]["/"].is_absolute()
    assert normalized["static_assets"]["/foo"].is_absolute()


def test_input_not_imported_shim_message() -> None:
    shim = InputNotImportedShim()
    with pytest.raises(AttributeError, match="not imported"):
        _ = shim.x


def test_run_express_basic_ui(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    _write_express_app(app_file, "ui.h1('Hello')")

    result = run_express(app_file)
    assert isinstance(result, (Tag, TagList))


def test_run_express_attribute_error_wrapped(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    _write_express_app(app_file, "ui.nope")

    with pytest.raises(RuntimeError, match="no attribute"):
        run_express(app_file)


def test_run_express_rejects_core_app_var(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text(
        "\n".join(
            [
                "from shiny import App",
                "from shiny.express import ui",
                "app = App(ui=ui.h1('x'), server=None)",
                "ui.h1('x')",
            ]
        )
    )

    with pytest.raises(RuntimeError, match="Shiny Express app"):
        run_express(app_file)


def test_create_express_app_merges_options(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    www_dir = tmp_path / "www"
    assets_dir = tmp_path / "assets"
    www_dir.mkdir()
    assets_dir.mkdir()

    _write_express_app(
        app_file,
        "app_opts(static_assets={'/foo': 'assets'}, bookmark_store='url', debug=True)\n"
        "ui.h1('Hello')",
    )

    app = create_express_app(app_file, "app_pkg")
    assert app.bookmark_store == "url"
    assert "/" in app._static_assets
    assert "/foo" in app._static_assets
    assert app._static_assets["/"].is_absolute()
    assert app._static_assets["/foo"].is_absolute()
