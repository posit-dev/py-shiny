import json
from pathlib import Path

from click.testing import CliRunner
from playwright.sync_api import Page

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
