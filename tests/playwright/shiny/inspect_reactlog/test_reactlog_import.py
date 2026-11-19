import json
import re
from pathlib import Path

from click.testing import CliRunner
from playwright.sync_api import Page, expect

from shiny._inspect import format_reactlog_html, load_reactlog_json
from shiny._main import main


def test_cli_report_and_browser_import_replay_the_same_r_trace(
    page: Page, tmp_path: Path
) -> None:
    trace = [
        {"action": "define", "reactId": "r1", "type": "reactiveVal"},
        {"action": "define", "reactId": "r2", "type": "observer"},
        {"action": "isolateEnter"},
        {"action": "dependsOn", "reactId": "r2", "depOnReactId": "r1"},
        {"action": "isolateExit"},
        {"action": "enter", "reactId": "r2"},
        {"action": "exit", "reactId": "r2"},
    ]
    source = tmp_path / "trace.json"
    source.write_text(json.dumps(trace))
    html = tmp_path / "trace.html"
    result = CliRunner().invoke(main, ["inspect", str(source), "--html", str(html)])
    assert result.exit_code == 0, result.output
    page.goto(html.as_uri())
    graph = "() => ({nodes: reactlogData.nodes, edges: reactlogData.edges, events: reactlogData.events})"
    cli = page.evaluate(graph)
    assert cli["edges"] == [{"from": "r1", "to": "r2", "isolated": True}]
    assert [event["action"] for event in cli["events"]] == [e["action"] for e in trace]
    assert cli["events"][-2]["provenance"] == "observed"
    page.evaluate("trace => loadReactlogObject(trace)", trace)
    assert page.evaluate(graph) == cli


def test_python_report_replays_dependency_switch(page: Page) -> None:
    log = [
        {"action": "define", "reactId": "a", "type": "input"},
        {"action": "define", "reactId": "b", "type": "input"},
        {"action": "define", "reactId": "calc", "type": "observable"},
        {"action": "dependsOn", "reactId": "calc", "depOnReactId": "a"},
        {"action": "dependsOnRemove", "reactId": "calc", "depOnReactId": "a"},
        {"action": "dependsOn", "reactId": "calc", "depOnReactId": "b"},
    ]
    report = load_reactlog_json({"trace_version": 1, "log": log})
    assert report["trace_version"] == 1
    page.set_content(format_reactlog_html(report, ""))
    edge_a = page.locator('.graph-edge[data-from="a"][data-to="calc"]')
    edge_b = page.locator('.graph-edge[data-from="b"][data-to="calc"]')

    for step, active in [(3, edge_a), (5, edge_b), (3, edge_a)]:
        page.evaluate("step => seekTo(step)", step)
        expect(active).not_to_have_class(re.compile(r"\bis-inactive\b"))
        expect(edge_b if active is edge_a else edge_a).to_have_class(
            re.compile(r"\bis-inactive\b")
        )


def test_cli_rejects_unknown_trace_version(tmp_path: Path) -> None:
    source = tmp_path / "incompatible.json"
    source.write_text(json.dumps({"trace_version": 2, "log": []}))
    html = tmp_path / "trace.html"

    result = CliRunner().invoke(main, ["inspect", str(source), "--html", str(html)])

    assert result.exit_code != 0
    assert "Unsupported Reactlog trace version: 2" in result.output
    assert not html.exists()
