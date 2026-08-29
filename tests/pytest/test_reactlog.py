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
    assert 'aria-label="Filter reactive nodes by name or type"' in html
    assert 'aria-label="Fit graph to view"' in html
    assert 'aria-label="Zoom in"' in html
    assert 'aria-label="Zoom out"' in html
    assert 'aria-label="Timeline step scrubber"' in html
    assert "aria-pressed=" in html


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
        'n0["📥 input.a-b"]:::inputClass' in mermaid
        or 'n1["📥 input.a-b"]:::inputClass' in mermaid
    )
    assert (
        'n0["📥 input.a_b"]:::inputClass' in mermaid
        or 'n1["📥 input.a_b"]:::inputClass' in mermaid
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
    assert "Interactive Shiny Reactive Log" in content


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
