from __future__ import annotations

import io
import json
import time
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
    monkeypatch.setattr(cli, "_wait_for_enter", lambda: None)
    monkeypatch.setattr(cli, "_is_interactive", lambda: True)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")

    res = CliRunner().invoke(
        main,
        ["reactlog", str(app), "--no-browser", "--json", str(tmp_path / "o.json")],
        input="2\n",
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
        input="",
    )
    assert res.exit_code == 0, res.output
    assert (tmp_path / "o-aaaaaaaa.json").is_file() and (
        tmp_path / "o-bbbbbbbb.json"
    ).is_file()


def test_reactlog_cli_no_browser_without_tty_exports_newest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sessions = [  # newest first
        {"id": "a" * 64, "start": 2.0, "end": None},
        {"id": "b" * 64, "start": 1.0, "end": 1.5},
    ]

    def fake_serve(
        app_file: Path,
        *,
        on_ready: Callable[[str], None],
        wait: Callable[[], None],
        choose: Callable[[list[dict[str, Any]]], list[str]],
    ) -> list[dict[str, Any]]:
        wait()
        return [dict(SAVED, session=i) for i in choose(sessions)]

    monkeypatch.setattr(cli, "serve_and_collect", fake_serve)
    monkeypatch.setattr(cli, "_wait_for_enter", lambda: None)
    monkeypatch.setattr(cli, "_is_interactive", lambda: False)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    out = tmp_path / "o.json"

    res = CliRunner().invoke(
        main, ["reactlog", str(app), "--no-browser", "--json", str(out)], input=""
    )
    assert res.exit_code == 0, res.output
    assert json.loads(out.read_text())["session"] == "a" * 64
    assert (
        "2 sessions were recorded; exported the newest (pass --all to export all)."
        in res.output
    )


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


def test_wait_for_enter_returns_on_ctrl_c_without_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def interrupt(secs: float) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    monkeypatch.setattr(time, "sleep", interrupt)
    cli._wait_for_enter()  # pyright: ignore[reportPrivateUsage]


def test_reactlog_cli_redacts_saved_json(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    res = CliRunner().invoke(
        main, ["reactlog", str(_saved(tmp_path)), "--redact-inputs", "--json", str(out)]
    )
    assert res.exit_code == 0, res.output
    values = [e["value"] for e in json.loads(out.read_text())["log"] if "value" in e]
    assert values == ["[REDACTED]"]


def test_reactlog_cli_creates_output_dirs(tmp_path: Path) -> None:
    out = tmp_path / "new" / "dir" / "out.json"
    res = CliRunner().invoke(
        main, ["reactlog", str(_saved(tmp_path)), "--json", str(out)]
    )
    assert res.exit_code == 0, res.output
    assert out.is_file()


def test_reactlog_cli_unwritable_output(tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("")
    res = CliRunner().invoke(
        main, ["reactlog", str(_saved(tmp_path)), "--json", str(blocker / "o.json")]
    )
    assert res.exit_code == 1
    assert "Could not write" in res.output and "Traceback" not in res.output


@pytest.mark.parametrize("content", ["not json", "[1, 2]", '{"log": 3}'])
def test_reactlog_cli_invalid_saved_json(tmp_path: Path, content: str) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(content)
    res = CliRunner().invoke(
        main, ["reactlog", str(bad), "--json", str(tmp_path / "o.json")]
    )
    assert res.exit_code == 1
    assert "Not a reactlog JSON file" in res.output and "Traceback" not in res.output


@pytest.mark.parametrize(
    "flags, saved",
    [
        (["--video", "v.webm", "--no-browser"], False),
        (["--all"], False),
        (["--no-browser"], True),
        (["--video", "v.webm"], True),
        (["--all"], True),
    ],
)
def test_reactlog_cli_rejects_inapplicable_flags(
    tmp_path: Path, flags: list[str], saved: bool
) -> None:
    target = _saved(tmp_path) if saved else tmp_path / "app.py"
    if not saved:
        target.write_text("from shiny.express import ui\n")
    res = CliRunner().invoke(main, ["reactlog", str(target), *flags])
    assert res.exit_code == 2, res.output


def test_reactlog_cli_rejects_duplicate_outputs(tmp_path: Path) -> None:
    out = tmp_path / "out"
    res = CliRunner().invoke(
        main,
        ["reactlog", str(_saved(tmp_path)), "--html", str(out), "--json", str(out)],
    )
    assert res.exit_code == 1
    assert "more than one output" in res.output


def test_reactlog_cli_writes_generated_test(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    actions = [
        {
            "type": "input",
            "name": "n",
            "value": 7,
            "binding": "shiny.sliderInput",
            "tag": "INPUT",
            "elType": "text",
            "classes": "",
            "container": "",
        }
    ]

    def fake_record(app_file: Path, **kw: Any) -> Recording:
        return Recording(export=SAVED, actions=actions, session_id="s1")

    monkeypatch.setattr(cli, "record_session", fake_record)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    test_file = tmp_path / "test_app.py"
    res = CliRunner().invoke(
        main,
        [
            "reactlog",
            str(app),
            "--json",
            str(tmp_path / "o.json"),
            "--test",
            str(test_file),
        ],
    )
    assert res.exit_code == 0, res.output
    assert 'controller.InputSlider(page, "n").set("7")' in test_file.read_text()
    assert "parametrize" not in test_file.read_text()  # test sits next to app.py


def test_reactlog_cli_generated_test_points_at_app(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_record(app_file: Path, **kw: Any) -> Recording:
        return Recording(export=SAVED, session_id="s1")

    monkeypatch.setattr(cli, "record_session", fake_record)
    app = tmp_path / "myapp" / "app.py"
    app.parent.mkdir()
    app.write_text("from shiny.express import ui\n")
    test_file = tmp_path / "tests" / "test_app.py"
    res = CliRunner().invoke(
        main,
        ["reactlog", str(app), "--json", str(tmp_path / "o.json")]
        + ["--test", str(test_file)],
    )
    assert res.exit_code == 0, res.output
    assert '"../myapp/app.py"' in test_file.read_text()


def test_reactlog_cli_replay_passes_script(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict[str, Any] = {}

    def fake_record(app_file: Path, **kw: Any) -> Recording:
        seen.update(kw)
        return Recording(export=SAVED, session_id="s1")

    monkeypatch.setattr(cli, "record_session", fake_record)
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    replay = tmp_path / "test_app.py"
    replay.write_text("def test_app(page, local_app):\n    pass\n")
    res = CliRunner().invoke(
        main,
        ["reactlog", str(app), "--json", str(tmp_path / "o.json")]
        + ["--replay", str(replay)],
    )
    assert res.exit_code == 0, res.output
    assert callable(seen["script"])


def test_reactlog_cli_test_output_cannot_overwrite_app(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    res = CliRunner().invoke(main, ["reactlog", str(app), "--test", str(app)])
    assert res.exit_code != 0
    assert "Refusing to overwrite" in res.output


def test_reactlog_cli_rejects_incompatible_flags(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    for flags in (
        ["--no-browser", "--test", "t.py"],
        ["--no-browser", "--replay", "t.py"],
        ["--test", "t.py", "--replay", "t.py"],
    ):
        res = CliRunner().invoke(main, ["reactlog", str(app), *flags])
        assert res.exit_code == 2, (flags, res.output)


def test_reactlog_cli_test_needs_an_app_file(tmp_path: Path) -> None:
    out = str(tmp_path / "test_app.py")
    for args in (
        ["--code", "from shiny.express import ui"],
        ["-"],
    ):
        res = CliRunner().invoke(
            main, ["reactlog", *args, "--test", out], input="from shiny import ui\n"
        )
        assert res.exit_code == 2, (args, res.output)
        assert "--test needs an app file" in res.output


def _fake_record(
    monkeypatch: pytest.MonkeyPatch, actions: list[dict[str, Any]] | None = None
) -> list[Path]:
    calls: list[Path] = []

    def fake_record(app_file: Path, **kw: Any) -> Recording:
        calls.append(app_file)
        return Recording(export=SAVED, actions=actions or [], session_id="s1")

    monkeypatch.setattr(cli, "record_session", fake_record)
    return calls


def _app(tmp_path: Path) -> Path:
    app = tmp_path / "app.py"
    app.write_text("from shiny.express import ui\n")
    return app


def test_reactlog_cli_redacted_test_hides_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_record(
        monkeypatch,
        [
            # Only the flag says the recording was redacted: clicks keep values.
            {"type": "input", "name": "go", "value": 1, "tag": "BUTTON"},
            {"type": "output", "name": "o", "binding": "shiny.textOutput"}
            | {"value": "secret", "tag": "DIV"},
        ],
    )
    test_file = tmp_path / "test_app.py"
    args = ["reactlog", str(_app(tmp_path)), "--json", str(tmp_path / "o.json")]
    res = CliRunner().invoke(main, args + ["--redact-inputs", "--test", str(test_file)])
    assert res.exit_code == 0, res.output
    assert "secret" not in test_file.read_text()
    assert "# o updated" in test_file.read_text()


def test_reactlog_cli_writes_reactlog_before_the_test(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_record(monkeypatch)
    blocker = tmp_path / "file"
    blocker.write_text("")
    out = tmp_path / "o.json"
    res = CliRunner().invoke(
        main,
        ["reactlog", str(_app(tmp_path)), "--json", str(out)]
        + ["--test", str(blocker / "test_app.py")],
    )
    assert res.exit_code == 1 and "Could not write" in res.output
    assert out.is_file()


def test_reactlog_cli_test_marker_falls_back_to_absolute_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def cross_drive(*args: Any) -> str:
        raise ValueError("path is on mount 'C:', start on mount 'D:'")

    _fake_record(monkeypatch)
    monkeypatch.setattr(cli.os.path, "relpath", cross_drive)
    app = _app(tmp_path)
    test_file = tmp_path / "tests" / "test_app.py"
    res = CliRunner().invoke(
        main,
        ["reactlog", str(app), "--json", str(tmp_path / "o.json")]
        + ["--test", str(test_file)],
    )
    assert res.exit_code == 0, res.output
    assert f'"{app.resolve().as_posix()}"' in test_file.read_text()


def test_reactlog_cli_outputs_cannot_overwrite_replay_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _fake_record(monkeypatch)
    replay = tmp_path / "test_app.py"
    replay.write_text("def test_app(page, local_app):\n    pass\n")
    res = CliRunner().invoke(
        main,
        ["reactlog", str(_app(tmp_path)), "--replay", str(replay)]
        + ["--json", str(replay)],
    )
    assert res.exit_code == 1 and "Refusing to overwrite" in res.output
    assert not calls and replay.read_text().startswith("def test_app")


def test_reactlog_cli_test_refuses_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _fake_record(monkeypatch)
    test_file = tmp_path / "test_app.py"
    test_file.write_text("# refined by hand\n")
    res = CliRunner().invoke(
        main,
        ["reactlog", str(_app(tmp_path)), "--json", str(tmp_path / "o.json")]
        + ["--test", str(test_file)],
    )
    assert res.exit_code == 1
    assert "already exists" in res.output and "Traceback" not in res.output
    assert not calls and test_file.read_text() == "# refined by hand\n"
