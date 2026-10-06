from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Callable
from urllib.parse import urlencode

import pytest
from click.testing import CliRunner
from starlette.requests import Request
from starlette.testclient import TestClient
from starlette.types import Message

from shiny import App, Inputs, Outputs, Session, reactive, ui
from shiny._connection import MockConnection
from shiny._main import _run, main
from shiny.express._utils import escape_to_var_name
from shiny.reactive._trace import hooks
from shiny.session._session import AppSession


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
@pytest.mark.parametrize(
    "option,expected", [(None, True), (True, True), (False, False)]
)
@pytest.mark.parametrize("existing_app", [False, True])
def test_reactlog_runner_preserves_config_unless_overridden(
    monkeypatch: pytest.MonkeyPatch,
    option: bool | None,
    expected: bool,
    existing_app: bool,
) -> None:
    monkeypatch.setenv("SHINY_REACTLOG", "1")
    app = App(ui.page_fluid("test"), None)

    def serve(target: Any, **kwargs: Any) -> None:
        loaded = target if existing_app else App(ui.page_fluid("test"), None)
        response = TestClient(loaded.starlette_app).get("/__reactlog__")
        assert (response.status_code == 200) is expected

    monkeypatch.setattr(_run, "_run_uvicorn", serve)
    target = app if existing_app else "test_app:app"
    if option is None:
        _run.run_app(target, dev_mode=False)
    else:
        _run.run_app(target, dev_mode=False, reactlog=option)
    assert os.environ["SHINY_REACTLOG"] == "1"


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_runner_preserves_explicit_app_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SHINY_REACTLOG", raising=False)
    app = App(ui.page_fluid("test"), None, reactlog=True)

    def serve(target: Any, **kwargs: Any) -> None:
        assert TestClient(target.starlette_app).get("/__reactlog__").status_code == 200

    monkeypatch.setattr(_run, "_run_uvicorn", serve)
    _run.run_app(app, dev_mode=False)
    assert "SHINY_REACTLOG" not in os.environ


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_runner_enables_existing_disabled_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = App(ui.page_fluid("test"), None, reactlog=False)
    statuses: list[int] = []

    def serve(target: Any, **kwargs: Any) -> None:
        statuses.append(
            TestClient(target.starlette_app).get("/__reactlog__").status_code
        )

    monkeypatch.setattr(_run, "_run_uvicorn", serve)
    _run.run_app(app, dev_mode=False, reactlog=True)
    _run.run_app(app, dev_mode=False, reactlog=False)
    assert statuses == [200, 404]


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_proxied_requests_are_not_local() -> None:
    def server(input: Any, output: Any, session: Any) -> None:
        "REACTLOG_SOURCE_MARKER"

    app = App(ui.page_fluid("test"), server, reactlog=True)
    session = app._create_session(MockConnection())
    client = TestClient(app.starlette_app)
    proxied = {"X-Forwarded-For": "203.0.113.5"}
    url = f"/__reactlog__?session_id={session.id}"

    assert "REACTLOG_SOURCE_MARKER" in client.get(url).text
    assert client.get(url, headers=proxied).status_code == 403

    response = client.get(f"{url}&token={app.reactlog_token}", headers=proxied)
    assert response.status_code == 200
    assert "REACTLOG_SOURCE_MARKER" not in response.text


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_script_uses_relative_urls() -> None:
    app = App(ui.page_fluid("test"), None, reactlog=True)
    page = TestClient(app.starlette_app).get("/").text
    assert "'__reactlog__?token=" in page
    assert "'__reactlog__/mark?token=" in page
    assert "'/__reactlog__" not in page


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
@pytest.mark.parametrize(
    "flags,expected", [([], True), (["--reactlog"], True), (["--no-reactlog"], False)]
)
def test_reactlog_cli_respects_environment(
    monkeypatch: pytest.MonkeyPatch, flags: list[str], expected: bool
) -> None:
    monkeypatch.setenv("SHINY_REACTLOG", "1")

    def serve(target: Any, **kwargs: Any) -> None:
        app = App(ui.page_fluid("test"), None)
        assert (
            TestClient(app.starlette_app).get("/__reactlog__").status_code == 200
        ) is expected

    monkeypatch.setattr(_run, "_run_uvicorn", serve)
    result = CliRunner().invoke(main, ["run", "test_app:app", *flags])
    assert result.exit_code == 0, result.exception
    assert os.environ["SHINY_REACTLOG"] == "1"


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


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_toggle_installs_and_removes_tracer() -> None:
    def subscribed(rec: object) -> bool:
        return any(getattr(cb, "__self__", None) is rec for cb in hooks.add_dependency)

    app = App(ui.TagList(), None, reactlog=False)
    assert app._reactlog_recorder is None
    app.reactlog_enabled = True
    rec = app._reactlog_recorder
    assert rec is not None and subscribed(rec)
    app.reactlog_enabled = False
    assert app._reactlog_recorder is None and not subscribed(rec)


def _reactlog_request(
    app: App,
    *,
    path: str = "/__reactlog__",
    session_id: str | None = None,
    local: bool = False,
    method: str = "GET",
    body: bytes = b"",
) -> Request:
    """A reactlog request; non-local ones authenticate with the app's token."""
    query: dict[str, str] = {} if local else {"token": app.reactlog_token}
    if session_id is not None:
        query["session_id"] = session_id
    sent = False

    async def receive() -> Message:
        nonlocal sent
        if sent:
            return {"type": "http.disconnect"}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(
        {
            "type": "http",
            "method": method,
            "path": path,
            "headers": [(b"content-type", b"application/json")],
            "query_string": urlencode(query).encode(),
            "client": ("127.0.0.1", 1) if local else ("203.0.113.5", 1),
        },
        receive=receive,
    )


def _viewer_payload(body: bytes | memoryview) -> tuple[dict[str, Any], str]:
    """The reactlog data and app source embedded in the viewer page."""
    text = bytes(body).decode()
    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(text.split("const reactlogData = ", 1)[1])
    source, _ = decoder.raw_decode(text.split("const rawAppSource = ", 1)[1])
    return data, source


@asynccontextmanager
async def _live_session(
    app: App, init: dict[str, Any], ready: Callable[[list[dict[str, Any]]], bool]
) -> AsyncGenerator[AppSession, None]:
    """Run a mock session until its recorded log satisfies `ready`."""
    conn = MockConnection()
    sess = app._create_session(conn)
    conn.cause_receive(json.dumps({"method": "init", "data": init}))
    task = asyncio.create_task(sess._run())
    recorder = app._reactlog_recorder
    assert recorder is not None
    try:
        for _ in range(500):
            if ready(recorder.export(sess.id)["log"]):
                break
            await asyncio.sleep(0.01)
        yield sess
    finally:
        conn.cause_disconnect()
        await task


def _entered(label: str) -> Callable[[list[dict[str, Any]]], bool]:
    return lambda log: any(x["action"] == "enter" and x["label"] == label for x in log)


@pytest.mark.asyncio
@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
async def test_reactlog_endpoint_shows_runtime_dependency() -> None:
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        "REACTLOG_SOURCE_MARKER"

        @reactive.effect
        def watcher() -> None:
            input[f"dyn_{1}"]()  # computed name: invisible to static analysis

    app = App(ui.TagList(), server, reactlog=True)
    try:
        async with _live_session(
            app, {"dyn_1": 5}, _entered("reactive.effect watcher")
        ) as sess:
            # Remote (token) request: no app source is embedded, so everything
            # below must come from the recorded runtime graph.
            response = await app._on_reactlog_request_cb(
                _reactlog_request(app, session_id=sess.id)
            )
            data, source = _viewer_payload(response.body)
        assert source == ""
        assert data["trace_kind"] == "loaded_reactlog_json"
        ids = {n["label"]: n["id"] for n in data["nodes"]}
        assert {"input.dyn_1", "reactive.effect watcher"} <= ids.keys()
        assert {
            "from": ids["input.dyn_1"],
            "to": ids["reactive.effect watcher"],
        } in data["edges"]
        # The ended session stays viewable, now with an end time.
        recorder = app._reactlog_recorder
        assert recorder is not None
        info = recorder.session(sess.id)
        assert info is not None and info.end is not None
        response = await app._on_reactlog_request_cb(
            _reactlog_request(app, session_id=sess.id)
        )
        data, _ = _viewer_payload(response.body)
        assert "input.dyn_1" in {n["label"] for n in data["nodes"]}
    finally:
        app.reactlog_enabled = False


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_without_session_id_redirects_to_only_session() -> None:
    app = App(ui.TagList(), None, reactlog=True)
    try:
        session = app._create_session(MockConnection())
        client = TestClient(app.starlette_app)
        response = client.get("/__reactlog__", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == f"?session_id={session.id}"
    finally:
        app.reactlog_enabled = False


@pytest.mark.asyncio
@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
async def test_reactlog_without_session_id_lists_sessions_for_local_users() -> None:
    app = App(ui.TagList(), None, reactlog=True)
    try:
        client = TestClient(app.starlette_app)
        empty = client.get("/__reactlog__").text
        assert "No sessions recorded yet" in empty

        first = app._create_session(MockConnection())
        second = app._create_session(MockConnection())
        app._remove_session(first)
        page = client.get("/__reactlog__").text
        assert "choose a session" in page
        # Newest first; the ended session shows an end time, the live one "Active".
        assert page.index(second.id) < page.index(first.id)
        assert page.count("Active") == 1
        assert f'href="?session_id={first.id}"' in page

        unknown = client.get("/__reactlog__?session_id=nope").text
        assert "Session 'nope' was not found." in unknown

        # Session ids grant access to session routes: never list them remotely.
        remote = await app._on_reactlog_request_cb(_reactlog_request(app))
        assert second.id not in bytes(remote.body).decode()
    finally:
        app.reactlog_enabled = False


@pytest.mark.asyncio
@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
async def test_reactlog_endpoint_shows_posted_marks() -> None:
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def watcher() -> None:
            input.x()

    app = App(ui.TagList(), server, reactlog=True)
    try:
        async with _live_session(
            app, {"x": 1}, _entered("reactive.effect watcher")
        ) as sess:
            posted = await app._on_reactlog_mark_cb(
                _reactlog_request(
                    app,
                    path="/__reactlog__/mark",
                    session_id=sess.id,
                    method="POST",
                    body=b'{"label": "checkpoint"}',
                )
            )
            assert json.loads(bytes(posted.body)) == {
                "status": "ok",
                "marks_count": 1,
            }
            response = await app._on_reactlog_request_cb(
                _reactlog_request(app, session_id=sess.id)
            )
            data, _ = _viewer_payload(response.body)
        marks = [e for e in data["events"] if e["action"] == "userMark"]
        assert len(marks) == 1
        assert marks[0]["node_label"] == "🔖 checkpoint"
        assert marks[0]["mark_wave"]["is_mark"] is True
        assert marks[0]["mark_wave"]["trigger"] == "Bookmark: checkpoint"
    finally:
        app.reactlog_enabled = False


@pytest.mark.asyncio
@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
async def test_reactlog_remote_requests_must_name_the_session() -> None:
    app = App(ui.TagList(), None, reactlog=True)
    try:
        sess = app._create_session(MockConnection())
        sess._reactlog_marks.append({"action": "userMark", "label": "private"})
        path = "/__reactlog__/mark"

        async def labels(request: Request) -> list[str]:
            response = await app._on_reactlog_mark_cb(request)
            return [m["label"] for m in json.loads(bytes(response.body))["marks"]]

        assert await labels(_reactlog_request(app, path=path, local=True)) == [
            "private"
        ]
        assert await labels(_reactlog_request(app, path=path)) == []
        assert await labels(_reactlog_request(app, path=path, session_id=sess.id)) == [
            "private"
        ]
    finally:
        app.reactlog_enabled = False


@pytest.mark.asyncio
@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
async def test_reactlog_export_endpoint() -> None:
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def watcher() -> None:
            input.x()

    app = App(ui.TagList(), server, reactlog=True)
    try:
        async with _live_session(
            app, {"x": 1}, _entered("reactive.effect watcher")
        ) as sess:
            local = await app._on_reactlog_export_cb(
                _reactlog_request(
                    app, path="/__reactlog__/export", session_id=sess.id, local=True
                )
            )
            remote = await app._on_reactlog_export_cb(
                _reactlog_request(app, path="/__reactlog__/export", session_id=sess.id)
            )
            missing = await app._on_reactlog_export_cb(
                _reactlog_request(
                    app, path="/__reactlog__/export", session_id="nope", local=True
                )
            )
        local_data = json.loads(bytes(local.body))
        remote_data = json.loads(bytes(remote.body))
        watcher = next(
            x
            for x in local_data["log"]
            if x["action"] == "define" and x["label"] == "reactive.effect watcher"
        )
        assert watcher["source_file"] == "test_main_run.py"
        assert (
            "test_reactlog_export_endpoint" in local_data["sources"]["test_main_run.py"]
        )
        assert remote_data["sources"] == {}
        assert not any(
            str(x.get("source_file", "")).startswith("/") for x in remote_data["log"]
        )
        assert missing.status_code == 404
    finally:
        app.reactlog_enabled = False


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_sessions_endpoint_is_local_only() -> None:
    app = App(ui.TagList(), None, reactlog=True)
    try:
        session = app._create_session(MockConnection())
        client = TestClient(app.starlette_app)
        listed = client.get("/__reactlog__/sessions").json()
        assert [s["id"] for s in listed] == [session.id]
        assert listed[0]["end"] is None
        proxied = client.get(
            f"/__reactlog__/sessions?token={app.reactlog_token}",
            headers={"X-Forwarded-For": "203.0.113.5"},
        )
        assert proxied.status_code == 403
    finally:
        app.reactlog_enabled = False


@pytest.mark.asyncio
@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
async def test_remote_reactlog_without_session_shows_empty_viewer() -> None:
    app = App(ui.TagList(), None, reactlog=True)
    try:
        app._create_session(MockConnection())
        response = await app._on_reactlog_request_cb(_reactlog_request(app))
        data, source = _viewer_payload(response.body)
        assert data["nodes"] == [] and source == ""
        assert data["summary"] == (
            "No session selected. Open this page with Cmd/Ctrl+F3 from the app, "
            "or pass session_id."
        )
    finally:
        app.reactlog_enabled = False
