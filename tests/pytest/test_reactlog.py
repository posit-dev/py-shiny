from __future__ import annotations

import json
import re
import runpy
import textwrap
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

import pytest
from click.testing import CliRunner
from starlette.testclient import TestClient

from shiny import App, module, reactive, render
from shiny._connection import MockConnection
from shiny._main import main
from shiny.reactive._reactlog._viewer import (
    format_graph_dot,
    format_graph_mermaid,
    format_reactlog_html,
    generate_reactlog,
    inspect_reactive_graph,
    load_reactlog_json,
)
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


class _TagCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: List[Tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))

    def has_tag(self, tag: str, **attrs: str) -> bool:
        return any(
            candidate == tag
            and all(candidate_attrs.get(key) == value for key, value in attrs.items())
            for candidate, candidate_attrs in self.tags
        )


def test_inspect_graph_roles():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_slider("n", "N", 1, 10, 5)

@reactive.calc
def doubled():
    return input.n() * 2

@reactive.effect
def log_val():
    print(doubled())

@render.text
def out():
    return f"Doubled is {doubled()}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True
    roles = {n["id"]: n["role"] for n in graph["nodes"]}
    assert roles["input:n"] == "source"
    assert roles["calc:doubled"] == "conductor"
    assert roles["effect:log_val"] == "observer"
    assert roles["output:out"] == "observer"


def test_topological_execution_order():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_slider("x", "X", 1, 10, 5)

@reactive.calc
def a_derived():
    return z_base() + 10

@reactive.calc
def z_base():
    return input.x() * 2

@render.text
def out():
    return f"Result: {a_derived()}"
"""
    reactlog = generate_reactlog(code, inputs={"x": 3})
    assert reactlog["success"] is True

    calc_events = [
        e["node_id"] for e in reactlog["events"] if e["event"] == "wouldEvaluate"
    ]
    assert "calc:z_base" in calc_events
    assert "calc:a_derived" in calc_events
    assert "output:out" in calc_events

    z_index = calc_events.index("calc:z_base")
    a_index = calc_events.index("calc:a_derived")
    out_index = calc_events.index("output:out")
    assert z_index < a_index < out_index


def test_node_id_collision_input_and_calc_same_name():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("value", "Value", 10)

@reactive.calc
def value():
    return input.value() * 2

@render.text
def value():
    return f"Final {value()}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True
    node_ids = {n["id"] for n in graph["nodes"]}
    assert "input:value" in node_ids
    assert "calc:value" in node_ids
    assert "output:value" in node_ids
    assert len(graph["nodes"]) == 3

    edges = [(e["from"], e["to"]) for e in graph["edges"]]
    assert ("input:value", "calc:value") in edges
    assert ("calc:value", "output:value") in edges


def test_generate_reactlog_with_recorded_actions():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_slider("count", "Count", 1, 100, 20)

@reactive.calc
def triple():
    return input.count() * 3

@render.text
def display():
    return f"Value is {triple()}"
"""
    actions = [
        {
            "type": "input",
            "name": "count",
            "value": 45,
            "inputType": "shiny.sliderInput",
            "timestamp": 120,
        },
        {"type": "click", "target": "submit_btn", "text": "Submit", "timestamp": 250},
        {"type": "output", "name": "display", "timestamp": 310},
    ]

    reactlog = generate_reactlog(code, recorded_actions=actions, video_path="demo.webm")
    assert reactlog["success"] is True
    assert reactlog["trace_kind"] == "inferred_simulation_with_recorded_browser_events"
    assert reactlog["video_path"] == "demo.webm"
    assert reactlog["observed_events_count"] == 3
    assert reactlog["inferred_events_count"] > 0

    event_types = [e["event"] for e in reactlog["events"]]
    assert "analysisInit" in event_types
    assert "define" in event_types
    assert "inputChange" in event_types
    assert "userClick" in event_types
    assert "outputUpdated" in event_types
    assert "recordingComplete" in event_types


def test_deduplicate_input_actions():
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 1)
@render.text
def out():
    return str(input.val())
"""
    actions = [
        {"type": "input", "name": "val", "value": 10, "timestamp": 100},
        {
            "type": "input",
            "name": "val",
            "value": 10,
            "timestamp": 120,
        },  # duplicate within 20ms
        {"type": "input", "name": "val", "value": 20, "timestamp": 600},  # new value
    ]
    reactlog = generate_reactlog(code, recorded_actions=actions)
    input_changes = [e for e in reactlog["events"] if e["event"] == "inputChange"]
    assert len(input_changes) == 2
    assert input_changes[0]["value"] == "10"
    assert input_changes[1]["value"] == "20"


def test_observed_vs_inferred_provenance_labels():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("n", "N", 5)
@reactive.calc
def double():
    return input.n() * 2
@render.text
def out():
    return str(double())
"""
    actions = [
        {"type": "input", "name": "n", "value": 15, "timestamp": 200},
        {"type": "output", "name": "out", "timestamp": 300},
    ]
    reactlog = generate_reactlog(code, recorded_actions=actions)
    for e in reactlog["events"]:
        assert e.get("provenance") in ("observed", "inferred")

    html = format_reactlog_html(reactlog, source_code=code)
    assert "provenance-observed" in html
    assert "provenance-inferred" in html
    assert "Observed:" in html
    assert "Inferred:" in html


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
    assert 'aria-label="Filter reactive nodes by name, type, or id"' in html
    assert 'aria-label="Fit graph to view"' in html
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


def test_format_reactlog_html_semantic_tags():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    parser = _TagCollector()
    parser.feed(html)
    assert parser.has_tag("header")
    assert parser.has_tag("main")
    assert parser.has_tag("aside")
    assert parser.has_tag("button")


def test_format_reactlog_html_graph_visible_on_initialization():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert ".graph-edge" in html
    assert "opacity: 0.75;" in html
    assert ".graph-edge { opacity: 0;" not in html


def test_reactlog_phase_separation_and_skip():
    reactlog = _chain_log(5, 42)
    assert reactlog["init_steps_count"] > 0
    assert reactlog["interaction_steps_count"] > 0

    html = format_reactlog_html(
        reactlog, source_code=_CHAIN_SOURCE, video_path="/tmp/recording.webm"
    )
    assert "phase-selector" in html
    assert "btn-skip-init" in html
    assert "skipToInteractions()" in html
    assert "setupVideoSync()" in html


def test_format_mermaid_and_dot():
    graph = _chain_log()
    mermaid = format_graph_mermaid(graph)
    assert "graph TD" in mermaid
    n = _mermaid_id(mermaid, "input.n")
    doubled = _mermaid_id(mermaid, "reactive.calc doubled")
    out = _mermaid_id(mermaid, "output out")
    assert f"{n} --> {doubled}" in mermaid
    assert f"{doubled} --> {out}" in mermaid

    dot = format_graph_dot(graph)
    assert "digraph ReactiveGraph" in dot
    assert f'"{n}" -> "{doubled}";' in dot


def test_mermaid_and_dot_hyphen_underscore_collision():
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
    dot = format_graph_dot(graph)
    assert 'label="input.a-b"' in dot
    assert 'label="input.a_b"' in dot


def test_unresolved_inputs_creates_source_nodes():
    code = """from shiny.express import input, render

@render.text
def result():
    return f"Hello {input.customer()}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True
    node_ids = {n["id"] for n in graph["nodes"]}
    assert "input:customer" in node_ids
    assert "output:result" in node_ids

    inp_node = next(n for n in graph["nodes"] if n["id"] == "input:customer")
    assert inp_node["declaration"] == "unresolved"
    assert inp_node["role"] == "source"

    edges = [(e["from"], e["to"]) for e in graph["edges"]]
    assert ("input:customer", "output:result") in edges


def test_inferred_events_count_includes_recording_complete():
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greet():
    return f"Hi {input.name()}"
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "name", "value": "Alice", "timestamp": 100}
        ],
    )
    inferred_events = [
        e for e in reactlog["events"] if e.get("provenance") == "inferred"
    ]
    assert reactlog["inferred_events_count"] == len(inferred_events)


def test_exact_edge_highlighting_with_multiple_dependencies():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("a", "A", 1)
ui.input_numeric("b", "B", 2)

@reactive.calc
def total():
    return input.a() + input.b()

@render.text
def out():
    return str(total())
"""
    actions = [
        {"type": "input", "name": "a", "value": 10, "timestamp": 100},
    ]
    reactlog = generate_reactlog(code, recorded_actions=actions)
    propagate_events = [e for e in reactlog["events"] if e["event"] == "propagate"]
    assert len(propagate_events) >= 1
    first_prop = propagate_events[0]
    assert first_prop["edge_from"] == "input:a"
    assert first_prop["edge_to"] == "calc:total"

    depends_events = [e for e in reactlog["events"] if e["event"] == "dependsOn"]
    assert any(
        e.get("edge_from") == "input:a" and e.get("edge_to") == "calc:total"
        for e in depends_events
    )
    assert any(
        e.get("edge_from") == "input:b" and e.get("edge_to") == "calc:total"
        for e in depends_events
    )


def test_format_reactlog_html_has_draggable_splitter():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert 'id="split-resizer"' in html
    assert 'class="resizer-handle"' in html
    assert 'aria-label="Resize sidebar panel"' in html
    assert "initSplitResizer()" in html
    assert "--sidebar-width" in html


def test_html_trace_timeline_ribbon():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)
    assert 'id="trace-timeline-bar"' in html
    assert 'id="trace-track-wrap"' in html
    assert 'id="trace-playhead"' in html
    assert "initTraceTimeline()" in html


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


def test_load_reactlog_json_with_r_reactlog_schema():
    r_reactlog = {
        "version": "1.0",
        "session": "session_abc",
        "log": [
            {
                "action": "define",
                "id": "input:num",
                "label": "num",
                "type": "observable",
                "time": 0.01,
                "session": "session_abc",
            },
            {
                "action": "define",
                "id": "calc:double",
                "label": "double",
                "type": "calc",
                "time": 0.02,
                "session": "session_abc",
            },
            {
                "action": "dependsOn",
                "id": "calc:double",
                "dependsOn": "input:num",
                "time": 0.03,
                "session": "session_abc",
            },
            {
                "action": "define",
                "id": "output:txt",
                "label": "txt",
                "type": "observer",
                "time": 0.04,
                "session": "session_abc",
            },
            {
                "action": "dependsOn",
                "id": "output:txt",
                "dependsOn": "calc:double",
                "time": 0.05,
                "session": "session_abc",
            },
            {
                "action": "valueChange",
                "id": "input:num",
                "value": "42",
                "time": 1.0,
                "session": "session_abc",
            },
        ],
    }
    loaded = load_reactlog_json(r_reactlog)
    assert loaded["success"] is True
    assert len(loaded["nodes"]) == 3
    assert len(loaded["edges"]) == 2
    assert len(loaded["events"]) == 6

    input_node = next(n for n in loaded["nodes"] if n["id"] == "input:num")
    assert input_node["role"] == "source"
    assert input_node["type"] == "input"

    raw_events_list = r_reactlog["log"]
    loaded_raw = load_reactlog_json(raw_events_list)
    assert loaded_raw["success"] is True
    assert len(loaded_raw["nodes"]) == 3
    assert len(loaded_raw["edges"]) == 2


def test_format_reactlog_html_theme_support():
    reactlog = _chain_log()

    html_dark = format_reactlog_html(reactlog, source_code=_CHAIN_SOURCE, theme="dark")
    assert 'data-theme="dark"' in html_dark
    assert 'id="btn-theme-toggle"' in html_dark
    assert 'id="btn-open-json"' in html_dark

    html_light = format_reactlog_html(
        reactlog, source_code=_CHAIN_SOURCE, theme="light"
    )
    assert 'data-theme="light"' in html_light
    assert '[data-theme="light"]' in html_light
    assert "--bg: #f8fafc;" in html_light


def test_reactive_event_decorator_semantics():
    code = """from shiny import reactive
from shiny.express import input, render, ui

ui.input_action_button("go", "Go")
ui.input_text("secret", "Secret", value="hidden")

@reactive.effect
@reactive.event(input.go)
def update():
    x = input.secret()

@reactive.calc
@reactive.event(input.go)
def compute():
    return input.secret() + " computed"

@render.text
def txt():
    return compute()
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True

    edges = graph["edges"]
    assert {"from": "input:go", "to": "effect:update"} in edges
    assert {"from": "input:secret", "to": "effect:update"} not in edges

    assert {"from": "input:go", "to": "calc:compute"} in edges
    assert {"from": "input:secret", "to": "calc:compute"} not in edges

    assert {"from": "calc:compute", "to": "output:txt"} in edges


def test_reactive_event_multiple_triggers():
    code = """from shiny import reactive
from shiny.express import input, render

@reactive.calc
def base_val():
    return 10

@reactive.calc
@reactive.event(input.btn1, input.btn2, base_val)
def multi_triggered():
    body_val = input.ignored_input()
    return body_val * 2
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True

    edges = graph["edges"]
    assert {"from": "input:btn1", "to": "calc:multi_triggered"} in edges
    assert {"from": "input:btn2", "to": "calc:multi_triggered"} in edges
    assert {"from": "calc:base_val", "to": "calc:multi_triggered"} in edges
    assert {"from": "input:ignored_input", "to": "calc:multi_triggered"} not in edges


def test_reactive_isolate_block_semantics():
    code = """from shiny import reactive
from shiny.express import input, render

@render.text
def out():
    val_a = input.a()
    with reactive.isolate():
        val_b = input.b()
    return f"{val_a} {val_b}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True

    edges = graph["edges"]
    assert {"from": "input:a", "to": "output:out"} in edges
    assert {"from": "input:b", "to": "output:out", "isolated": True} in edges


@pytest.mark.parametrize("recorded", [False, True])
@pytest.mark.parametrize("changed", ["a", "b", "c"])
def test_isolated_reads_do_not_invalidate_downstream(recorded: bool, changed: str):
    code = """from shiny import reactive, render
@reactive.calc
def cached():
    return input.c()
@render.text
def out():
    value = input.a()
    with reactive.isolate():
        value += input.b() + cached()
    return str(value)
"""
    report = generate_reactlog(
        code,
        inputs={changed: 2},
        recorded_actions=(
            [{"type": "input", "name": changed, "value": 2, "timestamp": 1000}]
            if recorded
            else None
        ),
    )
    expected_nodes: dict[str, set[str]] = {
        "a": {"output:out"},
        "b": set(),
        "c": {"calc:cached"},
    }
    expected = expected_nodes[changed]
    for kind in ("propagate", "wouldEvaluate"):
        assert {
            e["node_id"] for e in report["events"] if e["event"] == kind
        } == expected
    assert {"from": "input:b", "to": "output:out", "isolated": True} in report["edges"]
    assert {"from": "calc:cached", "to": "output:out", "isolated": True} in report[
        "edges"
    ]
    assert not any(
        e["event"] == "dependsOn" and e["edge_from"] in ("input:b", "calc:cached")
        for e in report["events"]
    )
    if recorded:
        wave = report["action_waves"][-1]
        assert set(wave["invalidated_nodes"]) == expected
        assert set(wave["inferred_executions"]) == expected


def test_real_shiny_for_r_reactlog_parsing_and_epoch_time_normalization():
    r_reactlog = {
        "version": "1.0",
        "session": "r_session_123",
        "log": [
            {
                "action": "define",
                "reactId": "r1",
                "label": "input$num",
                "type": "observable",
                "time": 1650000000.100,
                "session": "r_session_123",
            },
            {
                "action": "define",
                "reactId": "r2",
                "label": "calc_double",
                "type": "calc",
                "time": 1650000000.250,
                "session": "r_session_123",
            },
            {
                "action": "define",
                "reactId": "r3",
                "label": "output$plot",
                "type": "observer",
                "time": 1650000000.300,
                "session": "r_session_123",
            },
            {
                "action": "dependsOn",
                "reactId": "r2",
                "depOnReactId": "r1",
                "time": 1650000000.400,
                "session": "r_session_123",
            },
            {
                "action": "dependsOn",
                "reactId": "r3",
                "depOnReactId": "r2",
                "time": 1650000000.500,
                "session": "r_session_123",
            },
            {
                "action": "valueChange",
                "reactId": "r1",
                "value": "99",
                "time": 1650000001.100,
                "session": "r_session_123",
            },
        ],
    }

    loaded = load_reactlog_json(r_reactlog)
    assert loaded["success"] is True
    assert len(loaded["nodes"]) == 3
    assert len(loaded["edges"]) == 2
    assert len(loaded["events"]) == 6

    assert {"from": "r1", "to": "r2"} in loaded["edges"]
    assert {"from": "r2", "to": "r3"} in loaded["edges"]

    events = loaded["events"]
    assert events[0]["time_sec"] == 0.0
    assert round(events[-1]["time_sec"], 1) == 1.0
    assert all(e["time_sec"] < 100.0 for e in events)


def test_reactlog_html_xss_protection_on_imported_data():
    malicious_log = {
        "version": "1.0",
        "session": "xss_session",
        "log": [
            {
                "action": "define",
                "reactId": "<img src=x onerror=alert(1)>",
                "label": "<script>alert('xss')</script>",
                "type": "observable",
                "time": 1.0,
                "details": "<b onmouseover=alert(2)>Click me</b>",
            },
            {
                "action": "define",
                "reactId": "out1",
                "label": "Safe Output",
                "type": "observer",
                "time": 1.5,
            },
            {
                "action": "dependsOn",
                "reactId": "out1",
                "depOnReactId": "<img src=x onerror=alert(1)>",
                "time": 2.0,
            },
        ],
    }

    html = format_reactlog_html(malicious_log, source_code="# test")
    assert "escapeHTML" in html
    assert (
        "<script>alert('xss')</script>" not in html
        or "\\u003c" in html
        or "\\u0022" in html
        or "escapeHTML" in html
    )


def test_reactlog_execution_debugger_elements_and_helpers():
    html = format_reactlog_html(_chain_log(), source_code=_CHAIN_SOURCE)

    assert "why-card" in html
    assert "why-story" in html
    assert "why-cascade-flow" in html
    assert "btn-focus-upstream" not in html
    assert "btn-focus-downstream" not in html
    assert "btn-focus-all" not in html
    assert "btn-summary-toggle" in html
    assert "recording-summary-popover" in html
    assert "actions-tab" in html
    assert "actions-panel" in html
    assert "action-list" in html
    assert "insp-source-drawer" in html
    assert "insp-upstream-list" in html
    assert "insp-downstream-list" in html
    assert "explainWhyNodeRan" in html
    assert "buildGraphIndices" in html
    assert "getUpstreamNodes" in html
    assert "getDownstreamNodes" in html
    assert "setFocusMode" not in html
    assert "renderInspector" in html
    assert "toggleSummaryPopover" in html
    assert "role-filter-dropdown" not in html
    assert "getActiveLineageSet" in html
    assert "filterLineageForNode" in html
    assert "timeline-mode-select" in html
    assert "trace-burst-ribbon" in html
    assert "trace-burst-track" in html
    assert "trace-seismograph" in html
    assert "playhead-pin" in html
    assert "trace-status-line" in html
    assert "setTimelineMode" in html
    assert "calculateTimePct" in html
    assert "renderSeismographLines" in html


def test_password_and_secret_inputs_redacted_at_ast_visitor():
    code = """from shiny.express import input, render, ui
ui.input_password("user_pass", "Password", value="super_secret_123")
ui.input_text("api_key_token", "API Key", value="sk-123456789")
ui.input_text("normal_user", "Username", value="admin")
@render.text
def out():
    return f"User: {input.normal_user()}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True
    defaults = graph.get("input_defaults", {})
    assert defaults.get("user_pass") == "[REDACTED]"
    assert defaults.get("api_key_token") == "[REDACTED]"
    assert defaults.get("normal_user") == "admin"


def test_authoritative_action_waves_in_reactlog():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("price", "Price", 25)
ui.input_numeric("units", "Units", 10)

@reactive.calc
def subtotal():
    return input.price() * input.units()

@render.text
def summary():
    return f"Subtotal: {subtotal()}"
"""
    actions = [
        {"type": "input", "name": "price", "value": 30, "timestamp": 200},
        {
            "type": "click",
            "name": "recalc_btn",
            "text": "Recalculate",
            "timestamp": 500,
        },
    ]
    reactlog = generate_reactlog(code, recorded_actions=actions)
    assert reactlog["success"] is True
    waves = reactlog.get("action_waves", [])
    assert len(waves) == 3

    init_w = waves[0]
    assert init_w["is_init"] is True
    assert init_w["trigger"] == "Init"

    price_w = waves[1]
    assert price_w["is_init"] is False
    assert "price" in price_w["trigger"]
    assert price_w["trigger_node_id"] == "input:price"
    assert "calc:subtotal" in price_w["invalidated_nodes"]
    assert "output:summary" in price_w["invalidated_nodes"]
    assert "calc:subtotal" in price_w["inferred_executions"]
    assert "output:summary" in price_w["observed_outputs"]

    click_w = waves[2]
    assert click_w["is_init"] is False
    assert "Click" in click_w["trigger"]


def test_semantic_states_in_events():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 5)

@reactive.calc
def doubled():
    return input.x() * 2

@render.text
def out():
    return str(doubled())
"""
    actions = [
        {"type": "input", "name": "x", "value": 10, "timestamp": 100},
        {"type": "output", "name": "out", "timestamp": 200},
    ]
    reactlog = generate_reactlog(code, recorded_actions=actions)
    events = reactlog["events"]

    define_evs = [e for e in events if e["event"] == "define"]
    for e in define_evs:
        assert e["semantic_state"] == "dependency_only"

    input_evs = [e for e in events if e["event"] == "inputChange"]
    for e in input_evs:
        assert e["semantic_state"] == "observed_execution"

    prop_evs = [e for e in events if e["event"] == "propagate"]
    for e in prop_evs:
        assert e["semantic_state"] == "invalidated"

    eval_evs = [e for e in events if e["event"] == "wouldEvaluate"]
    for e in eval_evs:
        assert e["semantic_state"] == "inferred_execution"


def test_source_code_html_includes_line_numbers():
    from shiny.reactive._reactlog._viewer import _format_python_source_html

    code = "from shiny.express import input, render, ui\n\nui.input_numeric('x', 'X', 10)\n"
    html = _format_python_source_html(code)
    assert 'class="source-line" data-line="1"' in html
    assert '<span class="source-line-num" aria-hidden="true">1</span>' in html
    assert 'class="source-line" data-line="3"' in html
    assert '<span class="source-line-num" aria-hidden="true">3</span>' in html


def test_r_reactlog_types_and_late_definitions():
    events = [
        {"action": "invalidateStart", "reactId": "r2"},
        {
            "action": "define",
            "reactId": "r1$x",
            "type": "reactiveValuesKey",
            "label": "input$x",
        },
        {"action": "define", "reactId": "r2", "type": "observable", "label": "doubled"},
        {
            "action": "define",
            "reactId": "r3",
            "type": "observer",
            "label": "output$result",
        },
        {
            "action": "define",
            "reactId": "r4",
            "type": "reactiveVal",
            "label": "counter",
        },
        {"action": "dependsOn", "reactId": "r2", "depOnReactId": "r1$x"},
        {"action": "dependsOn", "reactId": "r3", "depOnReactId": "r2"},
    ]
    result = load_reactlog_json(events)
    nodes = {n["id"]: n for n in result["nodes"]}
    assert nodes["r1$x"]["role"] == "source"
    assert nodes["r2"]["role"] == "conductor"
    assert nodes["r2"]["label"] == "doubled"
    assert nodes["r3"]["role"] == "observer"
    assert nodes["r4"]["role"] == "source"
    assert result["edges"] == [{"from": "r1$x", "to": "r2"}, {"from": "r2", "to": "r3"}]


def test_module_instances_and_cross_boundary_dependencies():
    code = """
from shiny import module, reactive, render, ui
@module.ui
def sales_ui():
    return ui.input_numeric("units", "Units", 10)
@module.server
def sales_server(input, output, session, factor):
    @reactive.calc
    def subtotal():
        return input.units() * factor()
    @render.plot
    def chart():
        return subtotal()
    return subtotal
sales_ui("west")
sales_ui("east")
def server(input, output, session):
    @reactive.calc
    def factor():
        return input.price()
    west = sales_server("west", factor)
    east = sales_server("east", factor=factor)
    @render.text
    def total():
        return west() + east()
"""
    result = inspect_reactive_graph(code)
    nodes = {n["id"]: n for n in result["nodes"]}
    edges = {(e["from"], e["to"]) for e in result["edges"]}
    for name in ("west", "east"):
        assert nodes[f"input:{name}-units"]["module"] == name
        assert nodes[f"input:{name}-units"]["value"] == 10
        assert nodes[f"output:{name}-chart"]["render_type"] == "plot"
        assert (f"input:{name}-units", f"calc:{name}-subtotal") in edges
        assert ("calc:factor", f"calc:{name}-subtotal") in edges
        assert (f"calc:{name}-subtotal", "output:total") in edges
    assert "calc:subtotal" not in nodes


def test_nested_modules_keep_distinct_namespaces():
    code = """
from shiny import module, reactive, render
@module.server
def child(input, output, session):
    @reactive.calc
    def value():
        return input.n()
    return value
@module.server
def parent(input, output, session):
    inner = child("inner")
    @render.text
    def result():
        return inner()
parent("one")
parent("two")
"""
    result = inspect_reactive_graph(code)
    nodes = {n["id"]: n for n in result["nodes"]}
    assert nodes["calc:one-inner-value"]["module"] == "one-inner"
    assert nodes["output:one-result"]["module"] == "one"
    assert {"from": "calc:two-inner-value", "to": "output:two-result"} in result[
        "edges"
    ]


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


def test_module_event_triggers_are_namespaced():
    result = inspect_reactive_graph("""
from shiny import module, reactive
@module.server
def controls(input, output, session):
    @reactive.effect
    @reactive.event(input.apply)
    def save():
        print(input.value())
controls("filters")
""")
    assert {"from": "input:filters-apply", "to": "effect:filters-save"} in result[
        "edges"
    ]
    assert not any(e["from"] == "input:filters-value" for e in result["edges"])


def test_multifile_circular_imports_and_duplicate_function_names(tmp_path: Path):
    code = """import first
import second
first.sales("one")
second.sales("two")
"""
    module_code = """import {other}
from shiny import module, reactive
@module.server
def sales(input, output, session):
    @reactive.calc
    def total():
        return input.{input_name}()
    return total
"""
    for name, other in (("first", "second"), ("second", "first")):
        (tmp_path / f"{name}.py").write_text(
            module_code.format(other=other, input_name=name)
        )
    app = tmp_path / "app.py"
    app.write_text(code)
    report = inspect_reactive_graph(code, source_path=app)
    assert {"from": "input:one-first", "to": "calc:one-total"} in report["edges"]
    assert {"from": "input:two-second", "to": "calc:two-total"} in report["edges"]
    assert len(report["sources"]) == 3


def test_multifile_reports_syntax_error_in_imported_file(tmp_path: Path):
    (tmp_path / "broken.py").write_text("def invalid(:\n")
    report = inspect_reactive_graph("import broken", source_path=tmp_path / "app.py")
    assert report["success"] is False
    assert "broken.py:1" in report["error"]


def test_load_reactlog_json_with_plot_preview():
    data = {
        "version": "1.0",
        "session": "test-session",
        "entry_file": "app.py",
        "sources": {"app.py": "from shiny import ui"},
        "events": [
            {
                "action": "output",
                "node_id": "output:plot",
                "node_label": "output:plot",
                "plot": {
                    "src": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
                    "alt": "Test Plot",
                },
            }
        ],
    }
    loaded = load_reactlog_json(data)
    assert loaded["success"] is True
    assert loaded["entry_file"] == "app.py"
    assert "app.py" in loaded["sources"]
    assert loaded["events"][0]["plot"]["alt"] == "Test Plot"
    assert loaded["events"][0]["plot"]["src"].startswith("data:image/png;base64")


def test_isolated_dependencies_marked_in_edges():
    code = """from shiny import reactive
from shiny.express import input, render

@reactive.calc
def isolated_calc():
    with reactive.isolate():
        val = input.untracked()
    return val + input.tracked()

@render.text
def txt():
    with reactive.isolate():
        return f"{input.isolated_out()}"
"""
    res = inspect_reactive_graph(code)
    assert res["success"] is True
    edges = res["edges"]
    assert {
        "from": "input:untracked",
        "to": "calc:isolated_calc",
        "isolated": True,
    } in edges
    assert {"from": "input:tracked", "to": "calc:isolated_calc"} in edges
    assert {
        "from": "input:isolated_out",
        "to": "output:txt",
        "isolated": True,
    } in edges


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


def test_reactive_marks_api_and_generate_reactlog():
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


def test_reactlog_html_features():
    html = format_reactlog_html(_chain_log(0, 1, 2, 3, 4), _CHAIN_SOURCE)
    assert "shortcuts-modal" in html
    assert "Isolated read" in html
    assert "arrow-isolated" in html
    assert "node-exec-badge" in html


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
    assert "F3" in resp.text

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


def test_interleaved_timeline_bookmarks():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 10)
ui.input_numeric("y", "Y", 20)

@render.text
def out():
    return f"val={input.x() + input.y()}"
"""
    recorded_actions = [
        {"type": "input", "name": "x", "value": 15, "timestamp": 1000},
        {"type": "input", "name": "y", "value": 25, "timestamp": 3000},
    ]
    marks = [
        {"action": "userMark", "label": "Start Mark", "time": 0.5, "timestamp": 500},
        {"action": "userMark", "label": "Middle Mark", "time": 2.0, "timestamp": 2000},
        {"action": "userMark", "label": "End Mark", "time": 4.0, "timestamp": 4000},
    ]

    rlog = generate_reactlog(code, recorded_actions=recorded_actions, marks=marks)
    assert rlog["success"] is True

    waves = rlog.get("action_waves", [])
    mark_waves = [w for w in waves if w.get("is_mark")]
    assert len(mark_waves) == 3

    labels = [w["trigger_label"] for w in waves]
    start_idx = next(i for i, l in enumerate(labels) if "Start Mark" in l)
    x_idx = next(i for i, l in enumerate(labels) if "x" in l)
    mid_idx = next(i for i, l in enumerate(labels) if "Middle Mark" in l)
    y_idx = next(i for i, l in enumerate(labels) if "y" in l)
    end_idx = next(i for i, l in enumerate(labels) if "End Mark" in l)

    assert start_idx < x_idx < mid_idx < y_idx < end_idx


def test_shiny_run_reactlog_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["run", "--help"])
    assert result.exit_code == 0
    assert "--reactlog" in result.output


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


@pytest.mark.usefixtures("no_leaked_reactlog_tracer")
def test_app_reactlog_explicit_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("SHINY_REACTLOG", raising=False)
    from shiny import App, ui

    app_disabled = App(ui.page_fluid("Off"), None, reactlog=False)
    assert app_disabled.reactlog_enabled is False

    app_enabled = App(ui.page_fluid("On"), None, reactlog=True)
    assert app_enabled.reactlog_enabled is True
    assert len(app_enabled.reactlog_token) > 10


def _recorded_view_source(app: App) -> str:
    """The app source a local user sees in a recorded session's "App code" tab."""
    session = app._create_session(MockConnection())
    response = TestClient(app.starlette_app).get(
        "/__reactlog__", params={"session_id": session.id}
    )
    assert response.status_code == 200
    source, _ = json.JSONDecoder().raw_decode(
        response.text.split("const rawAppSource = ", 1)[1]
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


def test_inspect_fully_qualified_shiny_decorators():
    code = """import shiny
shiny.ui.input_numeric("unused", "Unused", 7)
@shiny.reactive.calc
def doubled():
    return input.x() * 2
@shiny.render.text
def out():
    with shiny.reactive.isolate():
        extra = input.y()
    return str(doubled() + extra)
"""
    graph = inspect_reactive_graph(code)
    assert {n["id"] for n in graph["nodes"]} == {
        "input:unused",
        "input:x",
        "input:y",
        "calc:doubled",
        "output:out",
    }
    assert {"from": "input:x", "to": "calc:doubled"} in graph["edges"]
    assert {"from": "calc:doubled", "to": "output:out"} in graph["edges"]
    assert {"from": "input:y", "to": "output:out", "isolated": True} in graph["edges"]


@pytest.mark.parametrize("decorator", ["my_calculator", "side_effect", "prevent"])
def test_inspect_ignores_unrelated_decorator_names(decorator: str):
    graph = inspect_reactive_graph(
        f"@{decorator}\ndef helper():\n    return input.x()\n"
    )
    assert graph["nodes"] == []


def test_express_showcase_reactlog_features():
    app_file = Path(__file__).resolve().parent.parent.parent / "dist2" / "app.py"
    if not app_file.exists():
        return
    source = app_file.read_text(encoding="utf-8")
    report = generate_reactlog(source, source_path=app_file)
    assert report["success"] is True
    node_types = {n["type"] for n in report["nodes"]}
    assert {"input", "calc", "effect", "output"}.issubset(node_types)
    modules = {n.get("module") for n in report["nodes"] if n.get("module")}
    assert modules == {"solar", "wind"}
    isolated = [e for e in report["edges"] if e.get("isolated")]
    assert len(isolated) >= 1
    assert set(report["sources"].keys()) == {"app.py", "zone_module.py"}


def test_load_reactlog_json_marks_isolated_edges():
    data = {
        "log": [
            {
                "action": "define",
                "reactId": "r1",
                "label": "a",
                "type": "reactiveVal",
                "time": 1.0,
            },
            {
                "action": "define",
                "reactId": "r2",
                "label": "b",
                "type": "reactiveVal",
                "time": 1.0,
            },
            {
                "action": "define",
                "reactId": "r3",
                "label": "e",
                "type": "observer",
                "time": 1.0,
            },
            {
                "action": "dependsOn",
                "reactId": "r3",
                "depOnReactId": "r1",
                "isolate": True,
                "time": 2.0,
            },
            {
                "action": "dependsOn",
                "reactId": "r3",
                "depOnReactId": "r2",
                "isolate": False,
                "time": 2.0,
            },
        ]
    }
    out = load_reactlog_json(data)
    assert {(e["from"], e["to"], e.get("isolated", False)) for e in out["edges"]} == {
        ("r1", "r3", True),
        ("r2", "r3", False),
    }


def test_load_reactlog_json_mixed_isolation_on_same_edge_is_not_isolated():
    def dep(isolate: bool, t: float) -> Dict[str, Any]:
        return {
            "action": "dependsOn",
            "reactId": "r2",
            "depOnReactId": "r1",
            "isolate": isolate,
            "time": t,
        }

    out = load_reactlog_json({"log": [dep(True, 1.0), dep(False, 2.0)]})
    assert out["edges"] == [{"from": "r1", "to": "r2"}]


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


def test_load_reactlog_json_invalidate_start_is_an_invalidation():
    ev = next(e for e in _live_events() if e["action"] == "invalidateStart")
    assert ev["status"] == "affected"
    assert ev["details"] == "Invalidated 'reactive.effect e'"
    assert ev["semantic_state"] == "invalidated"


def test_load_reactlog_json_depends_on_remove_is_not_an_active_edge():
    ev = next(e for e in _live_events() if e["action"] == "dependsOnRemove")
    assert ev.get("edge_from") is None
    assert ev.get("dependsOn") is None
    assert ev["details"] == "Removed dependency: 'r1' no longer used by 'r2'"


def test_load_reactlog_json_recorded_inputs_are_sources():
    out = load_reactlog_json({"log": _live_log()})
    node = next(n for n in out["nodes"] if n["id"] == "r1")
    assert (node["role"], node["type"]) == ("source", "input")
    changes = [e for e in out["events"] if e["action"] == "valueChange"]
    assert [(e["node_type"], e["value"]) for e in changes] == [
        ("input", "1"),
        ("input", "2"),
    ]


def test_load_reactlog_json_marks_match_generated_marks():
    ev = next(e for e in _live_events() if e["action"] == "userMark")
    keys = ("event", "node_label", "node_type", "phase", "provenance", "details")
    assert {k: ev[k] for k in keys} == {
        "event": "userMark",
        "node_label": "\U0001f516 checkpoint",
        "node_type": "mark",
        "phase": "interaction",
        "provenance": "observed",
        "details": "User mark: checkpoint",
    }
    assert ev["mark_wave"]["is_mark"] is True
    assert ev["mark_wave"]["trigger"] == "Bookmark: checkpoint"


def test_reactlog_viewer_builds_waves_for_recorded_inputs_and_marks():
    # The viewer computes waves client-side for loaded logs; pin the hooks it keys on.
    html = format_reactlog_html(load_reactlog_json({"log": _live_log()}), "")
    assert "evAction === 'userMark' && ev.mark_wave" in html
    assert "ev.type === 'input' || ev.node_type === 'input'" in html


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


def test_saved_r_reactlog_initial_flush_is_init_phase() -> None:
    # R's reactlog also ends the initial flush with `queueEmpty`.
    raw = [
        {"action": "define", "reactId": "r1", "type": "reactiveValuesKey"},
        {"action": "valueChange", "reactId": "r1", "value": "1"},
        {"action": "enter", "reactId": "r2"},
        {"action": "exit", "reactId": "r2"},
        {"action": "queueEmpty"},
        {"action": "valueChange", "reactId": "r1", "value": "2"},
        {"action": "enter", "reactId": "r2"},
    ]
    phases = [e["phase"] for e in load_reactlog_json(raw)["events"]]
    assert phases == ["init"] * 5 + ["interaction"] * 2
    # A phase already in the log wins.
    raw[1]["phase"] = "interaction"
    assert load_reactlog_json(raw)["events"][1]["phase"] == "interaction"


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
