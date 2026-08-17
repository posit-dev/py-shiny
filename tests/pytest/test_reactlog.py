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


def test_inspect_graph_roles():
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_slider("n", "N", 1, 10, 5)

@reactive.calc
def doubled():
    return input.n() * 2

@render.text
def out():
    return f"Doubled is {doubled()}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True
    roles = {n["id"]: n["role"] for n in graph["nodes"]}
    assert roles["n"] == "source"
    assert roles["doubled"] == "conductor"
    assert roles["out"] == "observer"
    assert len(graph["edges"]) == 2


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

    events = [e["event"] for e in reactlog["events"]]
    assert "sessionInit" in events
    assert "define" in events
    assert "valueChange" in events
    assert "invalidate" in events
    assert "flushStart" in events
    assert "calculate" in events
    assert "dependsOn" in events
    assert "ready" in events
    assert "flushComplete" in events


def test_format_reactlog_html():
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code)
    html = format_reactlog_html(reactlog, title="Test Reactlog")
    assert "<!DOCTYPE html>" in html
    assert "Shiny Reactlog Visualizer" in html
    assert "LOG_DATA" in html


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
    assert "Reactlog Execution Trace" in res.output
    assert "sessionInit" in res.output
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
    assert "Shiny Reactlog Visualizer" in content


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
    val_events = [e for e in data["events"] if e["event"] == "valueChange"]
    assert len(val_events) == 1
    assert val_events[0]["value"] == "100"
