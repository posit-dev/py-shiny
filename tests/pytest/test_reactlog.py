from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

import pytest
from click.testing import CliRunner

from shiny._inspect import (
    format_graph_dot,
    format_graph_mermaid,
    format_reactlog_html,
    generate_reactlog,
    inspect_reactive_graph,
    load_reactlog_json,
)
from shiny._main import main


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
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(
        reactlog,
        source_code=code,
        video_path="/project/recordings/sub/session.webm",
        html_path="/project/reports/reactlog.html",
    )
    assert "../recordings/sub/session.webm" in html


def test_format_reactlog_html_self_contained_and_accessible():
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, source_code=code)
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
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(
        code, inputs={"name": "</script><script>alert('xss')</script>"}
    )
    html = format_reactlog_html(reactlog, source_code=code, title="Test Reactlog")
    assert "<!DOCTYPE html>" in html
    assert "</script><script>alert('xss')</script>" not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html


def test_format_reactlog_html_semantic_tags():
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, source_code=code)
    parser = _TagCollector()
    parser.feed(html)
    assert parser.has_tag("header")
    assert parser.has_tag("main")
    assert parser.has_tag("aside")
    assert parser.has_tag("button")


def test_format_reactlog_html_graph_visible_on_initialization():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("a", "A", 1)
@reactive.calc
def calc_b():
    return input.a() + 1
@render.text
def out_c():
    return str(calc_b())
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, source_code=code)
    assert ".graph-edge" in html
    assert "opacity: 0.75;" in html
    assert ".graph-edge { opacity: 0;" not in html


def test_reactlog_phase_separation_and_skip():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("n", "N", 5)
@reactive.calc
def calc_val():
    return input.n() * 2
@render.text
def out_val():
    return f"Val={calc_val()}"
"""
    recorded_actions = [
        {"type": "input", "name": "n", "value": 42, "timestamp": 1200},
        {"type": "output", "name": "out_val", "timestamp": 1500},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    assert reactlog["init_steps_count"] > 0
    assert reactlog["interaction_steps_count"] > 0
    assert reactlog["first_interaction_step"] == reactlog["init_steps_count"]

    html = format_reactlog_html(
        reactlog, source_code=code, video_path="/tmp/recording.webm"
    )
    assert "phase-selector" in html
    assert "btn-skip-init" in html
    assert "skipToInteractions()" in html
    assert "setupVideoSync()" in html


def test_format_mermaid_and_dot():
    code = """from shiny.express import input, render, ui
ui.input_slider("n", "N", 1, 10, 5)
@render.text
def txt():
    return f"Value: {input.n()}"
"""
    graph = inspect_reactive_graph(code)
    mermaid = format_graph_mermaid(graph)
    assert "graph TD" in mermaid
    assert "n0" in mermaid
    assert "n1" in mermaid
    assert "n0 --> n1" in mermaid

    dot = format_graph_dot(graph)
    assert "digraph ReactiveGraph" in dot
    assert '"n0" -> "n1";' in dot


def test_mermaid_and_dot_hyphen_underscore_collision():
    code = """from shiny.express import input, render, ui
ui.input_numeric("a_b", "A_B", 1)
ui.input_numeric("a-b", "A-B", 2)
@render.text
def out1():
    return str(input.a_b())
@render.text
def out2():
    return str(input["a-b"]())
"""
    graph = inspect_reactive_graph(code)
    mermaid = format_graph_mermaid(graph)
    assert (
        'n0["input.a-b"]:::inputClass' in mermaid
        or 'n1["input.a-b"]:::inputClass' in mermaid
    )
    assert (
        'n0["input.a_b"]:::inputClass' in mermaid
        or 'n1["input.a_b"]:::inputClass' in mermaid
    )
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


def test_cli_inspect_basic():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_slider("x", "X", 1, 5, 2)

@reactive.calc
def squared():
    return input.x() ** 2

@render.text
def result():
    return f"Res: {squared()}"
"""
    res = runner.invoke(main, ["inspect", "--code", code])
    assert res.exit_code == 0
    assert "Reactive Dependency Graph" in res.output
    assert "Inputs (Sources):" in res.output
    assert "input.x" in res.output
    assert "squared" in res.output
    assert "result" in res.output


def test_cli_inspect_json():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V: {input.val()}"
"""
    res = runner.invoke(main, ["inspect", "--code", code, "--json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["success"] is True
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1


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
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V: {input.val()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, source_code=code)
    assert 'id="split-resizer"' in html
    assert 'class="resizer-handle"' in html
    assert 'aria-label="Resize sidebar panel"' in html
    assert "initSplitResizer()" in html
    assert "--sidebar-width" in html


def test_html_trace_timeline_ribbon():
    code = """from shiny.express import input, render, ui
ui.input_numeric("n", "N", 10)
@render.text
def out():
    return f"V={input.n()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, source_code=code)
    assert 'id="trace-timeline-bar"' in html
    assert 'id="trace-track-wrap"' in html
    assert 'id="trace-playhead"' in html
    assert "initTraceTimeline()" in html


def test_cli_inspect_json_clean_stdout(tmp_path: Path):
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny.express import input, render, ui
ui.input_numeric("n", "N", 10)
@render.text
def out():
    return f"Val={input.n()}"
""",
        encoding="utf-8",
    )
    runner = CliRunner()
    res = runner.invoke(main, ["inspect", str(app_file), "--json"])
    assert res.exit_code == 0
    json_start = res.output.find("{")
    assert json_start != -1
    data = json.loads(res.output[json_start:])
    assert data["success"] is True
    assert "events" in data
    assert len(data["nodes"]) == 2


def test_cli_inspect_record_json_clean_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny.express import input, render, ui
ui.input_numeric("n", "N", 10)
@render.text
def out():
    return f"Val={input.n()}"
""",
        encoding="utf-8",
    )
    import shiny._inspect as inspect_mod
    import shiny._main._inspect as main_inspect_mod

    def _mock_record(*args: object, **kwargs: object) -> dict[str, object]:
        return {
            "success": True,
            "actions": [{"type": "input", "name": "n", "value": 10, "timestamp": 100}],
            "video_path": None,
        }

    monkeypatch.setattr(inspect_mod, "record_shiny_session", _mock_record)
    monkeypatch.setattr(main_inspect_mod, "record_shiny_session", _mock_record)

    runner = CliRunner()
    res = runner.invoke(
        main,
        ["inspect", str(app_file), "--record", "--headless", "--json"],
    )
    assert res.exit_code == 0
    json_start = res.output.find("{")
    assert json_start != -1
    data = json.loads(res.output[json_start:])
    assert data["success"] is True
    assert "events" in data
    assert data["trace_kind"] == "inferred_simulation_with_recorded_browser_events"


def test_cli_inspect_reactlog():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_numeric("n", "N", 5)
@render.text
def show():
    return str(input.n())
"""
    res = runner.invoke(main, ["inspect", "--code", code, "--reactlog"])
    assert res.exit_code == 0
    assert "Reactive Event Log" in res.output
    assert "analysisInit" in res.output


def test_cli_inspect_html_export(tmp_path: Path):
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V: {input.val()}"
"""
    out_html = tmp_path / "custom_reactlog.html"
    res = runner.invoke(
        main,
        ["inspect", "--code", code, "--html", str(out_html)],
    )
    assert res.exit_code == 0
    assert out_html.is_file()
    content = out_html.read_text(encoding="utf-8")
    assert "Reactlog report" in content


def test_reactlog_json_contract_r_shiny_compatibility():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("n", "Number", 5)

@reactive.calc
def double():
    return input.n() * 2

@render.text
def txt():
    return str(double())
"""
    reactlog = generate_reactlog(code)
    assert reactlog["version"] == "1.0"
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
        assert "id" in ev
        assert "label" in ev
        assert "type" in ev
        assert "time" in ev
        assert "session" in ev


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
    code = """from shiny.express import input, render, ui
ui.input_numeric("n", "N", 5)
@render.text
def out():
    return str(input.n())
"""
    reactlog = generate_reactlog(code)

    html_dark = format_reactlog_html(reactlog, source_code=code, theme="dark")
    assert 'data-theme="dark"' in html_dark
    assert 'id="btn-theme-toggle"' in html_dark
    assert 'id="btn-open-json"' in html_dark

    html_light = format_reactlog_html(reactlog, source_code=code, theme="light")
    assert 'data-theme="light"' in html_light
    assert '[data-theme="light"]' in html_light
    assert "--bg: #f8fafc;" in html_light


def test_cli_inspect_theme_and_json_file(tmp_path: Path):
    r_reactlog = {
        "version": "1.0",
        "session": "s1",
        "log": [
            {
                "action": "define",
                "id": "input:x",
                "label": "x",
                "type": "observable",
                "time": 0.1,
            },
            {
                "action": "define",
                "id": "output:y",
                "label": "y",
                "type": "observer",
                "time": 0.2,
            },
            {
                "action": "dependsOn",
                "id": "output:y",
                "dependsOn": "input:x",
                "time": 0.3,
            },
        ],
    }
    json_file = tmp_path / "legacy.json"
    json_file.write_text(json.dumps(r_reactlog), encoding="utf-8")

    out_html = tmp_path / "legacy_out.html"
    runner = CliRunner()
    res = runner.invoke(
        main,
        ["inspect", str(json_file), "--html", str(out_html), "--theme", "light"],
    )
    assert res.exit_code == 0
    assert out_html.is_file()
    html_content = out_html.read_text(encoding="utf-8")
    assert 'data-theme="light"' in html_content
    assert "input:x" in html_content
    assert "output:y" in html_content


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
    assert {"from": "input:b", "to": "output:out"} not in edges


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


def test_cli_inspect_record_with_format_json_and_video_defaults(tmp_path: Path):
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny.express import input, render, ui
ui.input_numeric("x", "X", 10)
@render.text
def out():
    return str(input.x())
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    res = runner.invoke(main, ["inspect", str(app_file), "--format", "json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data.get("success") is True
    assert "nodes" in data
    assert "edges" in data
    assert "target" in data

    html_out = tmp_path / "plain_report.html"
    res_html = runner.invoke(main, ["inspect", str(app_file), "--html", str(html_out)])
    assert res_html.exit_code == 0
    html_text = html_out.read_text(encoding="utf-8")
    assert 'id="video-tab"' not in html_text


def test_reactlog_execution_debugger_elements_and_helpers():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("val", "Val", 10)
@reactive.calc
def computed():
    return input.val() * 2
@render.text
def out():
    return f"Computed: {computed()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, source_code=code)

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


def test_record_session_options_passive_by_default():
    import inspect as py_inspect

    from shiny._inspect import record_shiny_session
    from shiny._main._inspect import inspect as inspect_cli_fn

    sig_rec = py_inspect.signature(record_shiny_session)
    assert sig_rec.parameters["auto_interact"].default is False
    assert sig_rec.parameters["redact_inputs"].default is False

    cli_params = {p.name: p.default for p in inspect_cli_fn.params}
    assert cli_params["auto_interact"] is False
    assert cli_params["redact_inputs"] is False

    if inspect_cli_fn.callback:
        sig_cb = py_inspect.signature(inspect_cli_fn.callback)
        assert sig_cb.parameters["auto_interact"].default is False
        assert sig_cb.parameters["redact_inputs"].default is False


def test_source_code_html_includes_line_numbers():
    from shiny._inspect import _format_python_source_html

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
    code = """
from shiny import module, render
@module.server
def chart(input, output, session):
    @render.plot
    def result():
        return input.n()
chart("sales")
"""
    plot = {"src": "data:image/png;base64,aGVsbG8=", "alt": "Revenue"}
    report = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "output", "name": "sales-result", "timestamp": 100, "plot": plot}
        ],
    )
    observed = next(e for e in report["events"] if e["event"] == "outputUpdated")
    assert observed["plot"] == plot
    loaded = load_reactlog_json(json.dumps(report))
    node = next(n for n in loaded["nodes"] if n["id"] == "output:sales-result")
    assert node["module"] == "sales"
    assert node["render_type"] == "plot"
    assert any(e.get("plot") == plot for e in loaded["events"])
    unsafe = generate_reactlog(
        code,
        recorded_actions=[
            {
                "type": "output",
                "name": "sales-result",
                "plot": {"src": "https://example.com/tracker.png"},
            }
        ],
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


def test_multifile_modules_aliases_packages_and_source_locations(tmp_path: Path):
    package = tmp_path / "modules"
    package.mkdir()
    (package / "__init__.py").write_text("from .sales import panel as exported_panel\n")
    module_source = """from shiny import module, reactive, render, ui
raise RuntimeError("Inspection must never execute this module")
@module.ui
def panel():
    return ui.input_numeric("units", "Units", 10)
@module.server
def sales(input, output, session, price):
    @reactive.calc
    def total():
        return input.units() * price()
    @render.plot
    def chart():
        return total()
    return total
"""
    (package / "sales.py").write_text(module_source)
    code = """from shiny import reactive, render
from modules import exported_panel as panel
import modules.sales as sales_module
panel("west")
panel("east")
def server(input, output, session):
    @reactive.calc
    def price():
        return input.price()
    west = sales_module.sales("west", price)
    east = sales_module.sales("east", price=price)
    @render.text
    def combined():
        return west() + east()
"""
    app = tmp_path / "app.py"
    app.write_text(code)
    report = generate_reactlog(code, source_path=app)
    nodes = {n["id"]: n for n in report["nodes"]}
    assert nodes["input:west-units"]["source_file"] == "modules/sales.py"
    assert nodes["calc:west-total"]["line"] == 9
    assert nodes["output:west-chart"]["source_file"] == "modules/sales.py"
    assert nodes["output:combined"]["source_file"] == "app.py"
    assert {"from": "calc:east-total", "to": "output:combined"} in report["edges"]
    assert {"from": "calc:price", "to": "calc:west-total"} in report["edges"]
    assert report["sources"]["modules/sales.py"] == module_source
    loaded = load_reactlog_json(json.dumps(report))
    assert loaded["sources"] == report["sources"]
    assert (
        next(n for n in loaded["nodes"] if n["id"] == "calc:west-total")["source_file"]
        == "modules/sales.py"
    )
    result = CliRunner().invoke(main, ["inspect", str(app), "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["sources"] == report["sources"]


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


def test_reactive_marks_api_and_generate_reactlog():
    from shiny import reactive

    reactive.clear_marks()
    reactive.mark("checkpoint-1")
    assert len(reactive.get_marks()) == 1
    assert reactive.get_marks()[0]["label"] == "checkpoint-1"

    code = "from shiny.express import input\ninput.x()"
    rlog = generate_reactlog(code, marks=reactive.get_marks())
    assert rlog["success"] is True
    mark_events = [e for e in rlog["events"] if e.get("action") == "userMark"]
    assert len(mark_events) == 1
    assert mark_events[0]["details"] == "User mark: checkpoint-1"
    reactive.clear_marks()


def test_reactlog_html_features():
    code = "from shiny.express import input, render\n@render.text\ndef out():\n    return f'{input.x()}'"
    rlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "x", "value": 1, "timestamp": 10},
            {"type": "input", "name": "x", "value": 2, "timestamp": 20},
            {"type": "input", "name": "x", "value": 3, "timestamp": 30},
            {"type": "input", "name": "x", "value": 4, "timestamp": 40},
        ],
    )
    html = format_reactlog_html(rlog, code)
    assert "shortcuts-modal" in html
    assert "Isolated read" in html
    assert "arrow-isolated" in html
    assert "node-exec-badge" in html


def test_reactlog_server_routes_and_hotkey(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SHINY_REACTLOG", "1")
    from starlette.testclient import TestClient

    from shiny import App, ui

    app = App(ui.page_fluid("Hello"), None)
    starlette_app = app.init_starlette_app()
    client = TestClient(starlette_app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "/__reactlog__" in resp.text
    assert "F3" in resp.text

    rlog_resp = client.get("/__reactlog__")
    assert rlog_resp.status_code == 200
    assert "Reactlog report" in rlog_resp.text

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


def test_app_reactlog_explicit_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("SHINY_REACTLOG", raising=False)
    from shiny import App, ui

    app_disabled = App(ui.page_fluid("Off"), None, reactlog=False)
    assert app_disabled.reactlog_enabled is False

    app_enabled = App(ui.page_fluid("On"), None, reactlog=True)
    assert app_enabled.reactlog_enabled is True
    assert len(app_enabled.reactlog_token) > 10
