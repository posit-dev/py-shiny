from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from shiny._inspect import (
    format_reactlog_html,
    generate_reactlog,
    inspect_reactive_graph,
)
from shiny._main import main
from shiny._validate import validate_shiny_code


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


def test_generate_reactlog_event_stream():
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
    reactlog = generate_reactlog(code, inputs={"count": 50})
    assert reactlog["success"] is True
    assert len(reactlog["events"]) > 5
    assert reactlog["trace_kind"] == "static_dependency_simulation"

    events = [e["event"] for e in reactlog["events"]]
    assert "analysisInit" in events
    assert "define" in events
    assert "assumeValue" in events
    assert "propagate" in events
    assert "orderingStart" in events
    assert "wouldEvaluate" in events
    assert "dependsOn" in events
    assert "ordered" in events
    assert "orderingComplete" in events
    assert "calculate" not in events
    assert "ready" not in events
    assert all(
        "executing" not in event["details"].lower()
        and "completed" not in event["details"].lower()
        for event in reactlog["events"]
    )


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
    html = format_reactlog_html(reactlog, title="Test Reactlog")
    assert "<!DOCTYPE html>" in html
    assert "</script><script>alert('xss')</script>" not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html
    assert "textContent" in html


def test_core_shiny_output_id_order_independent():
    server_first_code = """from shiny import App, render, ui

def server(input, output, session):
    @render.text
    def summary():
        return "Summary"

app_ui = ui.page_fluid(
    ui.output_text("summary")
)

app = App(app_ui, server)
"""
    res1 = validate_shiny_code(server_first_code)
    assert res1["valid"] is True
    assert len([w for w in res1["warnings"] if w["code"] == "DUPLICATE_ID"]) == 0

    ui_first_code = """from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_text("summary")
)

def server(input, output, session):
    @render.text
    def summary():
        return "Summary"

app = App(app_ui, server)
"""
    res2 = validate_shiny_code(ui_first_code)
    assert res2["valid"] is True
    assert len([w for w in res2["warnings"] if w["code"] == "DUPLICATE_ID"]) == 0


def test_duplicate_output_id_detected():
    dup_code = """from shiny import App, ui

app_ui = ui.page_fluid(
    ui.output_text("summary"),
    ui.output_text("summary")
)
"""
    res = validate_shiny_code(dup_code)
    dup_warnings = [w for w in res["warnings"] if w["code"] == "DUPLICATE_ID"]
    assert len(dup_warnings) == 1


def test_cli_inspect_reactlog():
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
    res = runner.invoke(main, ["inspect", "--code", code, "--reactlog"])
    assert res.exit_code == 0
    assert "Static Dependency Simulation" in res.output
    assert "analysisInit" in res.output
    assert "squared" in res.output
    assert "result" in res.output


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
    assert "Static Shiny Dependency Simulation" in content


def test_cli_inspect_inputs_cascade():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_slider("a", "A", 1, 10, 2)
@render.text
def show():
    return f"A={input.a()}"
"""
    res = runner.invoke(
        main,
        ["inspect", "--code", code, "-i", "a=100", "--json"],
    )
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["success"] is True
    val_events = [e for e in data["events"] if e["event"] == "assumeValue"]
    assert len(val_events) == 1
    assert val_events[0]["value"] == "100"
