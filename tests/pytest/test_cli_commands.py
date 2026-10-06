from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pytest
from click.testing import CliRunner

from shiny._main import _reactlog as cli
from shiny._main import main
from shiny.reactive._reactlog._record import Recording, RecordingError

SAVED = {
    "version": "1",
    "session": "s1",
    "log": [
        {
            "action": "define",
            "reactId": "r1",
            "label": "input.n",
            "type": "input",
            "time": 0.0,
        },
        {
            "action": "define",
            "reactId": "r2",
            "label": "reactive.calc doubled",
            "type": "calc",
            "time": 0.0,
        },
        {
            "action": "dependsOn",
            "reactId": "r2",
            "depOnReactId": "r1",
            "isolate": False,
            "time": 0.1,
        },
        {
            "action": "valueChange",
            "reactId": "r1",
            "label": "input.n",
            "type": "input",
            "value": "3",
            "time": 0.2,
        },
    ],
    "sources": dict[str, str](),
}


def _saved(tmp_path: Path) -> Path:
    path = tmp_path / "saved.json"
    path.write_text(json.dumps(SAVED))
    return path


def test_reactlog_cli_loads_saved_json(tmp_path: Path) -> None:
    saved = _saved(tmp_path)
    html, mmd, out_json = tmp_path / "r.html", tmp_path / "r.mmd", tmp_path / "r.json"
    res = CliRunner().invoke(
        main,
        [
            "reactlog",
            str(saved),
            "--html",
            str(html),
            "--mermaid",
            str(mmd),
            "--json",
            str(out_json),
        ],
    )
    assert res.exit_code == 0, res.output
    assert "reactive.calc doubled" in html.read_text()
    assert "graph TD" in mmd.read_text() and "-->" in mmd.read_text()
    assert json.loads(out_json.read_text())["log"] == SAVED["log"]


def test_reactlog_cli_defaults_to_html(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    res = CliRunner().invoke(main, ["reactlog", str(_saved(tmp_path))])
    assert res.exit_code == 0, res.output
    assert (tmp_path / "reactlog.html").is_file()


def test_reactlog_cli_refuses_to_overwrite_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved = _saved(tmp_path)
    before = saved.read_text()
    res = CliRunner().invoke(main, ["reactlog", str(saved), "--json", str(saved)])
    assert res.exit_code == 1
    assert saved.read_text() == before

    # `--html app.py` treats app.py as the input, never as the output path.
    monkeypatch.chdir(tmp_path)

    def fake_record_simple(app_file: Path, **kw: Any) -> Recording:
        return Recording(export=SAVED, session_id="s1")

    monkeypatch.setattr(cli, "record_session", fake_record_simple)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    res = CliRunner().invoke(main, ["reactlog", "--html", str(app)])
    assert res.exit_code == 0, res.output
    assert app.read_text() == "from shiny.express import ui\n"
    assert (tmp_path / "reactlog.html").is_file()


def test_reactlog_cli_records_with_browser(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: dict[str, Any] = {}

    def fake_record(app_file: Path, **kwargs: Any) -> Recording:
        calls["app_file"], calls["kwargs"] = app_file, kwargs
        return Recording(export=SAVED, video_path=kwargs["video_path"], session_id="s1")

    monkeypatch.setattr(cli, "record_session", fake_record)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    html = tmp_path / "out.html"
    res = CliRunner().invoke(
        main, ["reactlog", str(app), "--html", str(html), "--redact-inputs"]
    )
    assert res.exit_code == 0, res.output
    assert calls["app_file"] == app
    assert calls["kwargs"]["video_path"] == html.with_suffix(".webm")
    assert calls["kwargs"]["redact_inputs"] is True
    assert "out.webm" in html.read_text()


def test_reactlog_cli_no_browser_picks_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sessions = [
        {"id": "a" * 64, "start": 2.0, "end": None},
        {"id": "b" * 64, "start": 1.0, "end": 1.5},
    ]
    chosen: list[list[str]] = []

    def fake_serve(
        app_file: Path,
        *,
        on_ready: Callable[[str], None],
        wait: Callable[[], None],
        choose: Callable[[list[dict[str, Any]]], list[str]],
    ) -> list[dict[str, Any]]:
        on_ready("http://127.0.0.1:9/")
        wait()
        ids = choose(sessions)
        chosen.append(ids)
        return [dict(SAVED, session=i) for i in ids]

    monkeypatch.setattr(cli, "serve_and_collect", fake_serve)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")

    res = CliRunner().invoke(
        main,
        ["reactlog", str(app), "--no-browser", "--json", str(tmp_path / "o.json")],
        input="\n2\n",
    )
    assert res.exit_code == 0, res.output
    assert "http://127.0.0.1:9/" in res.output
    assert chosen[-1] == ["b" * 64]

    res = CliRunner().invoke(
        main,
        [
            "reactlog",
            str(app),
            "--no-browser",
            "--all",
            "--json",
            str(tmp_path / "o.json"),
        ],
        input="\n",
    )
    assert res.exit_code == 0, res.output
    assert (tmp_path / "o-aaaaaaaa.json").is_file() and (
        tmp_path / "o-bbbbbbbb.json"
    ).is_file()


def test_reactlog_cli_reports_app_start_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing(app_file: Path, **kwargs: Any) -> Recording:
        raise RecordingError("Failed to start Shiny app app.py: SyntaxError")

    monkeypatch.setattr(cli, "record_session", failing)
    app = tmp_path / "app.py"
    app.write_text("def broken(:\n")
    res = CliRunner().invoke(main, ["reactlog", str(app)])
    assert res.exit_code == 1
    assert "Failed to start Shiny app" in res.output
    assert "Traceback" not in res.output
