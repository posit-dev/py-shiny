from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Tuple

from click.testing import CliRunner

from shiny._inspect import (
    format_graph_dot,
    format_graph_mermaid,
    format_reactlog_html,
    generate_reactlog,
    inspect_reactive_graph,
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
    assert roles["n"] == "source"
    assert roles["doubled"] == "conductor"
    assert roles["log_val"] == "observer"
    assert roles["out"] == "observer"


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
    assert "z_base" in calc_events
    assert "a_derived" in calc_events
    assert "out" in calc_events

    z_index = calc_events.index("z_base")
    a_index = calc_events.index("a_derived")
    out_index = calc_events.index("out")
    assert z_index < a_index < out_index


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
    assert reactlog["trace_kind"] == "playwright_recording"
    assert reactlog["video_path"] == "demo.webm"

    event_types = [e["event"] for e in reactlog["events"]]
    assert "analysisInit" in event_types
    assert "define" in event_types
    assert "inputChange" in event_types
    assert "userClick" in event_types
    assert "outputUpdated" in event_types
    assert "recordingComplete" in event_types


def test_format_reactlog_html_includes_video_panel():
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code, video_path="/path/to/my_recording.webm")
    html = format_reactlog_html(
        reactlog, source_code=code, video_path="/path/to/my_recording.webm"
    )

    assert "my_recording.webm" in html
    assert 'id="video-tab"' in html
    assert 'id="video-panel"' in html
    assert "<video" in html


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
    assert "n --> txt" in mermaid

    dot = format_graph_dot(graph)
    assert "digraph ReactiveGraph" in dot
    assert '"n" -> "txt";' in dot


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
