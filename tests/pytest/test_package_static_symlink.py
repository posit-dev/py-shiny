from __future__ import annotations

import os
from pathlib import Path

import pytest
from htmltools import HTMLDependency
from starlette.testclient import TestClient

from shiny import App, ui


def test_dependency_symlink_outside_source_is_served(tmp_path: Path) -> None:
    outside = tmp_path / "cache" / "app.css"
    outside.parent.mkdir()
    outside.write_text("body{color:red}", encoding="utf-8")
    source = tmp_path / "www"
    source.mkdir()

    try:
        os.symlink(outside, source / "app.css")
    except OSError as error:
        pytest.skip(f"Symlinks are unavailable: {error}")

    dep = HTMLDependency(
        "symdep",
        "1",
        source={"subdir": str(source)},
        stylesheet={"href": "app.css"},
        all_files=True,
    )
    app = App(ui.div("hi"), None)
    app._register_web_dependency(dep)
    href = dep.source_path_map(lib_prefix=app.lib_prefix)["href"]
    response = TestClient(app).get("/" + href + "/app.css")

    assert response.status_code == 200
    assert response.text == "body{color:red}"
