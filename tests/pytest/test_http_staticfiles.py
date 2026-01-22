"""Tests for shiny.http_staticfiles module."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest
from starlette.responses import Response


def test_staticfiles_native_branch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    if "pyodide" in sys.modules:
        monkeypatch.delitem(sys.modules, "pyodide", raising=False)

    mod = importlib.reload(importlib.import_module("shiny.http_staticfiles"))

    class FakeResponse(Response):
        def __init__(self):
            super().__init__("ok")
            self.headers["content-type"] = "text/plain"
            self.media_type = "text/plain"

    def fake_file_response(self, full_path, *args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        mod.starlette.staticfiles.StaticFiles,
        "file_response",
        fake_file_response,
    )
    monkeypatch.setattr(
        "shiny.http_staticfiles._utils.guess_mime_type", lambda *_: "text/javascript"
    )

    sf = mod.StaticFiles(directory=tmp_path)
    resp = sf.file_response(tmp_path / "file.js")
    assert resp.headers["content-type"].startswith("text/javascript")


def test_staticfiles_wasm_branch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sys.modules["pyodide"] = ModuleType("pyodide")
    mod = importlib.reload(importlib.import_module("shiny.http_staticfiles"))

    file_path = tmp_path / "test.txt"
    file_path.write_text("data")

    final, trailing = mod._traverse_url_path(tmp_path, ["test.txt"])  # type: ignore[attr-defined]
    assert final == file_path
    assert trailing is False

    bad_final, _ = mod._traverse_url_path(tmp_path, [".."])
    assert bad_final is None

    headers = mod._convert_headers({"X": "Y"}, "text/plain")
    assert (b"X", b"Y") in headers

    # Cleanup
    monkeypatch.delitem(sys.modules, "pyodide", raising=False)
    importlib.reload(importlib.import_module("shiny.http_staticfiles"))
