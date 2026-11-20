from __future__ import annotations

import json
import re
import runpy
import textwrap
from pathlib import Path
from typing import Any, Dict, List, cast

import pytest
from reactlog import (
    format_graph_mermaid,
    format_reactlog_html,
    load_reactlog_json,
)
from starlette.testclient import TestClient

from shiny import App, module, reactive, render
from shiny._connection import MockConnection
from tests.pytest._reactlog_fixtures import record_export, record_log

_CHAIN_SOURCE = """def server(input, output, session):
    @reactive.calc
    def doubled():
        return input.n() * 2

    @render.text
    def out():
        return f"Doubled is {doubled()}"
"""


def _chain_server(input: Any, output: Any, session: Any) -> None:
    @reactive.calc
    def doubled() -> Any:
        return input.n() * 2

    @render.text
    def out() -> str:
        return f"Doubled is {doubled()}"


def _chain_log(*values: Any) -> Dict[str, Any]:
    """A recorded `input.n -> doubled -> out` session: init with the first value,
    then one update per remaining value. Recorded `sources` (this test file) are
    dropped so HTML assertions only see the viewer's own markup."""
    first, *rest = values or (1,)
    steps = [{"n": first, ".clientdata_output_out_hidden": False}]
    data = record_log(_chain_server, [*steps, *({"n": v} for v in rest)])
    return {**data, "sources": {}}


def _mermaid_id(mermaid: str, label: str) -> str:
    match = re.search(rf'(n\d+)\["{re.escape(label)}"\]', mermaid)
    assert match is not None, label
    return match.group(1)


def test_relative_video_path_different_directories():
    html = format_reactlog_html(
        _chain_log(),
        source_code=_CHAIN_SOURCE,
        video_path="/project/recordings/sub/session.webm",
        html_path="/project/reports/reactlog.html",
    )
    assert "../recordings/sub/session.webm" in html


def test_format_reactlog_html_self_contained_and_accessible():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert "https://" not in html
    assert 'src="http' not in html
    assert 'href="http' not in html
    assert 'aria-label="Filter reactive nodes by name, type, id, or module"' in html
    assert 'aria-label="Full screen"' in html
    assert 'aria-label="Zoom in"' in html
    assert 'aria-label="Zoom out"' in html
    assert 'aria-label="Timeline step scrubber"' in html
    assert 'aria-label="Source file"' in html


def test_format_reactlog_html_escaping():
    reactlog = _chain_log("</script><script>alert('xss')</script>")
    html = format_reactlog_html(
        reactlog, source_code=_CHAIN_SOURCE, title="Test Reactlog"
    )
    assert "<!DOCTYPE html>" in html
    assert "</script><script>alert('xss')</script>" not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html


def test_reactlog_phase_separation():
    reactlog = _chain_log(5, 42)
    assert reactlog["init_steps_count"] > 0
    assert reactlog["interaction_steps_count"] > 0

    html = format_reactlog_html(
        reactlog, source_code=_CHAIN_SOURCE, video_path="/tmp/recording.webm"
    )
    assert 'id="phase-filter-select"' not in html
    assert "btn-skip-init" not in html
    assert "setupVideoSync()" in html


def test_format_mermaid():
    graph = _chain_log()
    mermaid = format_graph_mermaid(graph)
    assert "graph TD" in mermaid
    n = _mermaid_id(mermaid, "input.n")
    doubled = _mermaid_id(mermaid, "reactive.calc doubled")
    out = _mermaid_id(mermaid, "output out")
    assert f"{n} --> {doubled}" in mermaid
    assert f"{doubled} --> {out}" in mermaid


def test_mermaid_hyphen_underscore_collision():
    def server(input: Any, output: Any, session: Any) -> None:
        @render.text
        def out1() -> str:
            return str(input.a_b())

        @render.text
        def out2() -> str:
            return str(input["a-b"]())

    graph = record_log(
        server,
        [
            {
                "a_b": 1,
                "a-b": 2,
                ".clientdata_output_out1_hidden": False,
                ".clientdata_output_out2_hidden": False,
            }
        ],
    )
    mermaid = format_graph_mermaid(graph)
    hyphen = _mermaid_id(mermaid, "input.a-b")
    underscore = _mermaid_id(mermaid, "input.a_b")
    assert hyphen != underscore
    assert f'{hyphen}["input.a-b"]:::inputClass' in mermaid
    assert f'{underscore}["input.a_b"]:::inputClass' in mermaid


def test_reactlog_json_contract_r_shiny_compatibility():
    reactlog = record_export(
        _chain_server, [{"n": 5, ".clientdata_output_out_hidden": False}]
    )
    assert reactlog["version"] == "1"
    assert "session" in reactlog
    assert "log" in reactlog
    assert isinstance(reactlog["log"], list)
    raw_log = cast(List[Any], reactlog["log"])
    log_events: List[Dict[str, Any]] = [
        cast(Dict[str, Any], e) for e in raw_log if isinstance(e, dict)
    ]
    assert len(log_events) > 0

    actions: set[str] = {str(ev["action"]) for ev in log_events}
    assert "define" in actions
    assert "dependsOn" in actions

    for ev in log_events:
        assert "action" in ev
        assert "time" in ev
        assert "session" in ev
        if "reactId" in ev:
            assert "label" in ev
            assert "type" in ev


def test_plot_snapshots_and_module_metadata_survive_json_roundtrip():
    @module.server
    def chart(input: Any, output: Any, session: Any) -> None:
        @render.plot
        def result() -> None:
            return None

    def server(input: Any, output: Any, session: Any) -> None:
        chart("sales")

    def export_with_plot(plot: Dict[str, Any]) -> Dict[str, Any]:
        export = record_export(
            server, [{".clientdata_output_sales-result_hidden": False}]
        )
        define = next(
            e
            for e in export["log"]
            if e["action"] == "define" and e["label"] == "output sales:result"
        )
        assert define["module"] == "sales"
        export["log"].append(
            {
                "action": "valueChange",
                "reactId": define["reactId"],
                "label": define["label"],
                "type": "output",
                "time": export["log"][-1]["time"],
                "plot": plot,
            }
        )
        return export

    plot = {"src": "data:image/png;base64,aGVsbG8=", "alt": "Revenue"}
    loaded = load_reactlog_json(json.dumps(export_with_plot(plot)))
    node = next(n for n in loaded["nodes"] if n["label"] == "output sales:result")
    assert node["module"] == "sales"
    assert node["render_type"] == "plot"
    assert node["source_file"] == Path(__file__).name
    assert isinstance(node["line"], int)
    assert any(e.get("plot") == plot for e in loaded["events"])
    unsafe = load_reactlog_json(
        export_with_plot({"src": "https://example.com/tracker.png"})
    )
    assert not any("plot" in e for e in unsafe["events"])


def test_recorded_sources_reach_the_viewer():
    export = record_export(
        _chain_server, [{"n": 1, ".clientdata_output_out_hidden": False}]
    )
    loaded = load_reactlog_json(export)
    node = next(n for n in loaded["nodes"] if n["label"] == "reactive.calc doubled")
    assert node["source_file"] in loaded["sources"]
    html = format_reactlog_html(loaded, source_code=_CHAIN_SOURCE)
    # A line only this test file contains, JSON-embedded in the viewer data.
    assert json.dumps("def test_recorded_sources_reach_the_viewer():")[1:-1] in html


def test_reactive_marks_api_and_recorded_marks():
    from shiny import reactive

    reactive.clear_marks()
    reactive.mark("checkpoint-1")
    assert len(reactive.get_marks()) == 1
    assert reactive.get_marks()[0]["label"] == "checkpoint-1"

    reactive.clear_marks()

    def server(input: Any, output: Any, session: Any) -> None:
        reactive.mark("checkpoint-1")

    rlog = record_log(server, [{}])
    assert rlog["success"] is True
    mark_events = [e for e in rlog["events"] if e.get("action") == "userMark"]
    assert len(mark_events) == 1
    assert mark_events[0]["details"] == "User mark: checkpoint-1"
    assert Path(mark_events[0]["source_file"]).name == Path(__file__).name


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_server_routes_and_hotkey(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SHINY_REACTLOG", "1")
    from starlette.testclient import TestClient

    from shiny import App, ui

    app = App(ui.page_fluid("Hello"), None)
    starlette_app = app.init_starlette_app()
    client = TestClient(starlette_app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "__reactlog__?token=" in resp.text
    assert "F8" in resp.text

    rlog_resp = client.get("/__reactlog__")
    assert rlog_resp.status_code == 200
    assert "choose a session" in rlog_resp.text
    assert "No sessions recorded yet" in rlog_resp.text

    mark_resp = client.post("/__reactlog__/mark", json={"label": "test-mark"})
    assert mark_resp.status_code == 200
    assert mark_resp.json()["status"] == "ok"

    get_mark_resp = client.get("/__reactlog__/mark")
    assert get_mark_resp.status_code == 200
    assert get_mark_resp.json()["status"] == "ok"
    assert any(m["label"] == "test-mark" for m in get_mark_resp.json()["marks"])


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_reactlog_remote_security_access_control():
    from starlette.testclient import TestClient

    from shiny import App, ui

    app = App(ui.page_fluid("Security test"), None, reactlog=True)
    client_app = app.init_starlette_app()

    local_client = TestClient(client_app)
    assert local_client.get("/__reactlog__").status_code == 200

    def make_remote(asgi_app: Any, host: str = "192.168.1.100") -> Any:
        async def remote_app(scope: dict[str, Any], receive: Any, send: Any) -> None:
            if scope.get("type") == "http":
                scope = dict(scope)
                scope["client"] = (host, 50000)
            await asgi_app(scope, receive, send)

        return remote_app

    remote_client = TestClient(
        make_remote(client_app)
    )  # pyright: ignore[reportArgumentType]
    assert remote_client.get("/__reactlog__").status_code == 403
    assert remote_client.get("/__reactlog__/mark").status_code == 403

    assert (
        remote_client.get(f"/__reactlog__?token={app.reactlog_token}").status_code
        == 200
    )
    assert (
        remote_client.get(f"/__reactlog__/mark?token={app.reactlog_token}").status_code
        == 200
    )
    assert remote_client.get("/__reactlog__?token=invalid_token").status_code == 403


def test_reactive_marks_session_scoping_and_isolation():
    from shiny import reactive
    from shiny.session import session_context

    class MockSessionObj:
        name: str
        ns: object

        def __init__(self, name: str) -> None:
            self.name = name
            self.ns = None

    sess_a = MockSessionObj("a")
    sess_b = MockSessionObj("b")

    with session_context(sess_a):  # pyright: ignore[reportArgumentType]
        reactive.mark("mark-a-1")
        reactive.mark("mark-a-2")
        marks_a = reactive.get_marks()

    with session_context(sess_b):  # pyright: ignore[reportArgumentType]
        reactive.mark("mark-b-1")
        marks_b = reactive.get_marks()

    assert len(marks_a) == 2
    assert len(marks_b) == 1
    assert marks_a[0]["label"] == "mark-a-1"
    assert marks_b[0]["label"] == "mark-b-1"

    with session_context(sess_a):  # pyright: ignore[reportArgumentType]
        reactive.clear_marks()
        assert len(reactive.get_marks()) == 0

    with session_context(sess_b):  # pyright: ignore[reportArgumentType]
        assert len(reactive.get_marks()) == 1


def _recorded_view_source(app: App) -> str:
    """The app source a local user sees in a recorded session's "App code" tab."""
    session = app._create_session(MockConnection())
    response = TestClient(app.starlette_app).get(
        "/__reactlog__", params={"session_id": session.id}
    )
    assert response.status_code == 200
    source, _ = json.JSONDecoder().raw_decode(
        response.text.split("let rawAppSource = ", 1)[1]
    )
    return source


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_in_app_reactlog_reads_complete_source_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.syspath_prepend(  # pyright: ignore[reportUnknownMemberType]
        str(tmp_path)
    )
    (tmp_path / "review_module.py").write_text("""from shiny import module, render
@module.server
def panel(input, output, session):
    @render.text
    def total():
        return str(input.amount())
""")
    source = """from shiny import App, ui
from review_module import panel
app_ui = ui.page_fluid(ui.input_numeric("unused", "Unused", 7))
def server(input, output, session):
    panel("sales")
app = App(app_ui, server, reactlog=True)
"""
    app_file = tmp_path / "app.py"
    app_file.write_text(source)
    app = runpy.run_path(str(app_file))["app"]
    assert _recorded_view_source(app) == source


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_in_app_reactlog_dedents_source_fallback(monkeypatch: pytest.MonkeyPatch):
    from shiny import App, _app, ui

    def server(input: Any, output: Any, session: Any):
        pass

    def missing_file(fn: object) -> str:
        return "/missing/app.py"

    def available_source(fn: object) -> str:
        return "    def server(input, output, session):\n        @render.text\n        def out():\n            return input.x()\n"

    monkeypatch.setattr(_app.inspect, "getfile", missing_file)
    monkeypatch.setattr(_app.inspect, "getsource", available_source)
    app = App(ui.page_fluid(), server, reactlog=True)
    assert _recorded_view_source(app) == textwrap.dedent(available_source(server))


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_express_reactlog_reads_app_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    from shiny.express._run import wrap_express_app

    monkeypatch.setenv("SHINY_REACTLOG", "1")
    app_file = tmp_path / "app.py"
    source = """from shiny.express import input, render, ui
ui.input_numeric("amount", "Amount", 3)
@render.text
def total():
    return str(input.amount())
"""
    app_file.write_text(source)
    app = wrap_express_app(app_file)
    try:
        assert _recorded_view_source(app) == source
    finally:
        # The express app module stays in sys.modules, so the App is never collected.
        app.reactlog_enabled = False


def test_custom_session_inherits_private_reactlog_storage():
    from shiny import reactive
    from shiny._namespaces import Root
    from shiny.session import Session, session_context

    # A third-party implementation of the pre-reactlog abstract contract.
    def stub(*args: Any, **kwargs: Any) -> None:
        pass

    custom_type = type(
        "CustomSession",
        (Session,),
        {
            name: stub
            for name in Session.__abstractmethods__
            if name != "_reactlog_marks"
        },
    )
    first, second = custom_type(), custom_type()
    first.ns = second.ns = Root
    with session_context(first):
        reactive.mark("first")
    with session_context(second):
        reactive.mark("second")
    assert [m["label"] for m in reactive.get_marks(first)] == ["first"]
    assert [m["label"] for m in reactive.get_marks(second)] == ["second"]
    reactive.clear_marks(first)
    assert reactive.get_marks(first) == []
    assert [m["label"] for m in reactive.get_marks(second)] == ["second"]


# A live (recorded) reactlog, as produced by shiny.reactive._reactlog.ReactlogRecorder.
_LIVE_LOG: List[Dict[str, Any]] = [
    {"action": "define", "reactId": "r1", "label": "input.x", "type": "input"},
    {
        "action": "define",
        "reactId": "r2",
        "label": "reactive.effect e",
        "type": "observer",
    },
    {
        "action": "dependsOn",
        "reactId": "r2",
        "depOnReactId": "r1",
        "label": "reactive.effect e",
        "type": "observer",
        "isolate": False,
    },
    {
        "action": "valueChange",
        "reactId": "r1",
        "label": "input.x",
        "type": "input",
        "value": "1",
    },
    {"action": "userMark", "label": "checkpoint", "details": "checkpoint"},
    {
        "action": "valueChange",
        "reactId": "r1",
        "label": "input.x",
        "type": "input",
        "value": "2",
    },
    {
        "action": "invalidateStart",
        "reactId": "r2",
        "label": "reactive.effect e",
        "type": "observer",
    },
    {
        "action": "dependsOnRemove",
        "reactId": "r2",
        "depOnReactId": "r1",
        "label": "reactive.effect e",
        "type": "observer",
        "isolate": False,
    },
]


def _live_log() -> List[Dict[str, Any]]:
    return [
        {"provenance": "observed", "time": 1_700_000_000.0 + i, **entry}
        for i, entry in enumerate(_LIVE_LOG)
    ]


def _live_events() -> List[Dict[str, Any]]:
    return load_reactlog_json({"log": _live_log()})["events"]


def test_record_log_fixture_returns_real_graph() -> None:
    def server(input: Any, output: Any, session: Any) -> None:
        @reactive.calc
        def doubled() -> int:
            return input.n() * 2

        @render.text
        def out() -> str:
            return str(doubled())

    data = record_log(
        server, [{"n": 1, ".clientdata_output_out_hidden": False}, {"n": 2}]
    )
    labels = {n["label"] for n in data["nodes"]}
    assert {"input.n", "reactive.calc doubled", "output out"} <= labels
    assert any(e["event"] == "valueChange" for e in data["events"])


def test_recorded_initial_flush_is_init_phase() -> None:
    data = _chain_log(1, 2)
    events = data["events"]
    init_end = next(i for i, e in enumerate(events) if e["event"] == "queueEmpty")
    assert all(e["phase"] == "init" for e in events[: init_end + 1])
    assert events[init_end + 1 :], "expected post-init events"
    first_change = next(
        e for e in events[init_end + 1 :] if e["event"] == "valueChange"
    )
    assert first_change["node_label"] == "input.n"
    assert first_change["value"] == "2"
    assert first_change["phase"] == "interaction"


def test_recorded_module_attribution_of_inputs_and_client_data() -> None:
    @module.server
    def panel(input: Any, output: Any, session: Any) -> None:
        @render.plot
        def chart() -> None:
            return None

        @render.text
        def label() -> str:
            return str(input.n())

    def server(input: Any, output: Any, session: Any) -> None:
        panel("sales")

    export = record_export(
        server,
        [
            {
                "sales-n": 1,
                ".clientdata_output_sales-chart_hidden": False,
                ".clientdata_output_sales-label_hidden": False,
            }
        ],
    )
    defines = {e["label"]: e for e in export["log"] if e["action"] == "define"}
    # Shared client data, first read by the module's plot, is the root's.
    assert "module" not in defines[".clientdata_pixelratio"]
    # Created by the root from the init message, but it is the module's input.
    assert defines["input.sales-n"]["module"] == "sales"


def test_format_reactlog_html_graph_view_modes():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert 'id="module-filter-select"' not in html
    assert "setViewMode(" in html


def test_format_reactlog_html_node_interactions_and_layout() -> None:
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert "App · ${countText}" in html
    assert "App (no namespace)" not in html
    assert "width: min(440px, 48vw, calc(100% - 64px))" in html
    assert "g.ondblclick" in html
    assert "handleSearch(term)" in html
    assert ".graph-edge.is-connected" in html
    timeline_idx = html.index('id="trace-timeline-bar"')
    shortcuts_idx = html.index('id="btn-shortcuts"')
    assert shortcuts_idx < timeline_idx
    assert 'id="btn-graph-legend"' in html
    assert 'id="btn-shortcuts"' in html
    assert 'title="Keyboard shortcuts (?)"' in html
    assert ">Shortcuts</button>" not in html
    assert (
        "let currentViewMode = 'flush';" in html
        or 'let currentViewMode = "flush";' in html
        or 'var currentViewMode = "flush";' in html
    )


def test_format_reactlog_html_preserves_video_path():
    log = _chain_log()
    html = format_reactlog_html(
        log, source_code=_CHAIN_SOURCE, video_path="recording.webm"
    )
    assert 'id="video-panel"' in html
    assert 'id="session-video"' in html
    assert '"video_path": "recording.webm"' in html


def test_format_reactlog_html_secondary_timeline_and_invalidation():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert 'id="secondary-timeline-bar"' in html
    assert 'id="secondary-timeline-tag"' in html
    assert 'id="secondary-timeline-title"' in html
    assert 'id="secondary-timeline-meta"' in html
    assert 'id="secondary-timeline-chips"' in html
    assert 'id="btn-close-secondary-timeline"' in html
    assert "toggleSecondaryTimelineForFlush()" in html
    assert "openSecondaryTimelineForFlush(" in html
    assert "openSecondaryTimelineForNode(" in html
    assert "closeSecondaryTimeline()" in html
    assert "renderSecondaryTimeline()" in html
    assert ".timeline-marker.is-output" in html
    assert ".graph-node.is-invalidated" in html
    assert 'id="timeline-key"' in html
