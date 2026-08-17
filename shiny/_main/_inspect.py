from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import click

from .._inspect import (
    format_graph_dot,
    format_graph_mermaid,
    inspect_reactive_graph,
)
from ._utils import cli_bold, cli_code, cli_danger, cli_info


@click.command(
    "inspect",
    help="""Inspect and map the reactive dependency graph (DAG) of a Shiny app.

    Statically parses UI inputs, reactive calculations, effects, and outputs,
    and displays their dependency relationships.

    Examples:

        shiny inspect app.py
        shiny inspect app.py --mermaid
        shiny inspect app.py --json
    """,
)
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option("--code", type=str, default=None, help="Inline Python source code to inspect.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "mermaid", "dot"], case_sensitive=False),
    default="text",
    help="Output format (default: text).",
)
@click.option("--json", "json_flag", is_flag=True, default=False, help="Shorthand for --format json.")
@click.option("--mermaid", "mermaid_flag", is_flag=True, default=False, help="Shorthand for --format mermaid.")
def inspect(
    path: Optional[str],
    code: Optional[str],
    output_format: str,
    json_flag: bool,
    mermaid_flag: bool,
) -> None:
    if json_flag:
        output_format = "json"
    elif mermaid_flag:
        output_format = "mermaid"

    source_code: str = ""
    target_desc: str = ""

    if code is not None:
        source_code = code
        target_desc = "<inline code>"
    elif path == "-":
        source_code = sys.stdin.read()
        target_desc = "<stdin>"
    elif path is not None:
        p = Path(path)
        if p.is_dir():
            candidate = p / "app.py"
            if candidate.is_file():
                p = candidate
            else:
                py_files = list(p.glob("*.py"))
                if py_files:
                    p = py_files[0]
                else:
                    if output_format == "json":
                        click.echo(json.dumps({"success": False, "error": f"No Python files in directory: {path}"}))
                    else:
                        click.echo(cli_danger(f"No Python files found in directory: {path}"))
                    sys.exit(1)
        if not p.is_file():
            if output_format == "json":
                click.echo(json.dumps({"success": False, "error": f"File not found: {path}"}))
            else:
                click.echo(cli_danger(f"File not found: {path}"))
            sys.exit(1)
        source_code = p.read_text(encoding="utf-8")
        target_desc = str(p)
    else:
        default_app = Path("app.py")
        if default_app.is_file():
            source_code = default_app.read_text(encoding="utf-8")
            target_desc = "app.py"
        else:
            if output_format == "json":
                click.echo(json.dumps({"success": False, "error": "No file specified and app.py not found in current directory."}))
            else:
                click.echo(cli_danger("No file specified and app.py not found in current directory."))
            sys.exit(1)

    graph = inspect_reactive_graph(source_code)

    if not graph.get("success"):
        if output_format == "json":
            click.echo(json.dumps(graph, indent=2))
        else:
            click.echo(cli_danger(f"Failed to inspect reactive graph: {graph.get('error')}"))
        sys.exit(1)

    if output_format == "json":
        graph_with_target = dict(graph)
        graph_with_target["target"] = target_desc
        click.echo(json.dumps(graph_with_target, indent=2))
        sys.exit(0)
    elif output_format == "mermaid":
        click.echo(format_graph_mermaid(graph))
        sys.exit(0)
    elif output_format == "dot":
        click.echo(format_graph_dot(graph))
        sys.exit(0)
    else:
        click.echo(cli_bold(f"Reactive Dependency Graph for {target_desc}"))
        click.echo(cli_info(str(graph["summary"])) + "\n")

        nodes_by_type: Dict[str, List[str]] = {"input": [], "calc": [], "output": []}
        for n in graph.get("nodes", []):
            ntype: str = str(n.get("type", "calc"))
            nodes_by_type.setdefault(ntype, []).append(str(n["id"]))

        if nodes_by_type["input"]:
            click.echo(cli_bold("Inputs (Sources):"))
            for inp in nodes_by_type["input"]:
                click.echo(f"  📥 input.{inp}")
            click.echo("")

        if nodes_by_type["calc"]:
            click.echo(cli_bold("Reactive Calcs & Effects:"))
            for c in nodes_by_type["calc"]:
                click.echo(f"  ⚡ {c}")
            click.echo("")

        if nodes_by_type["output"]:
            click.echo(cli_bold("Outputs (Sinks):"))
            for out in nodes_by_type["output"]:
                click.echo(f"  📊 {out}")
            click.echo("")

        edges = graph.get("edges", [])
        if edges:
            click.echo(cli_bold("Dependency Flow:"))
            for e in edges:
                click.echo(f"  {cli_code(str(e['from']))}  \u27f6  {cli_bold(str(e['to']))}")
        else:
            click.echo(cli_info("No direct reactive dependencies detected."))

        sys.exit(0)
