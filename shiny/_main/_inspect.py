from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import click

from .._inspect import (
    format_graph_dot,
    format_graph_mermaid,
    format_reactlog_html,
    generate_reactlog,
)
from ._utils import cli_bold, cli_code, cli_danger, cli_info, cli_success


def _parse_input_value(val_str: str) -> Any:
    try:
        return json.loads(val_str)
    except Exception:
        if val_str.lower() in ("true", "false"):
            return val_str.lower() == "true"
        try:
            return int(val_str)
        except ValueError:
            try:
                return float(val_str)
            except ValueError:
                return val_str


@click.command(
    "inspect",
    help="""Inspect and map the reactive dependency graph (DAG) or Reactlog lifecycle of a Shiny app.

    Statically parses UI inputs, reactive calculations, effects, and outputs,
    and displays their dependency relationships or chronological Reactlog event trace.

    Examples:

        shiny inspect app.py
        shiny inspect app.py --mermaid
        shiny inspect app.py --reactlog
        shiny inspect app.py --html reactlog.html
        shiny inspect app.py -i n=50 --json
    """,
)
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option(
    "--code", type=str, default=None, help="Inline Python source code to inspect."
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(
        ["text", "json", "mermaid", "dot", "reactlog", "html"], case_sensitive=False
    ),
    default="text",
    help="Output format (default: text).",
)
@click.option(
    "--reactlog",
    "reactlog_flag",
    is_flag=True,
    default=False,
    help="Trace chronological Reactlog lifecycle events.",
)
@click.option(
    "--html",
    "html_out",
    type=click.Path(),
    default=None,
    help="Export interactive HTML Reactlog visualizer to file.",
)
@click.option(
    "--json",
    "json_flag",
    is_flag=True,
    default=False,
    help="Shorthand for --format json.",
)
@click.option(
    "--mermaid",
    "mermaid_flag",
    is_flag=True,
    default=False,
    help="Shorthand for --format mermaid.",
)
@click.option(
    "-i",
    "--input",
    "input_pairs",
    multiple=True,
    help="Set an input value as KEY=VALUE to simulate invalidations.",
)
@click.option(
    "--inputs",
    "inputs_json",
    type=str,
    default=None,
    help="JSON dictionary string of input values for Reactlog simulation.",
)
def inspect(
    path: Optional[str],
    code: Optional[str],
    output_format: str,
    reactlog_flag: bool,
    html_out: Optional[str],
    json_flag: bool,
    mermaid_flag: bool,
    input_pairs: tuple[str, ...],
    inputs_json: Optional[str],
) -> None:
    if json_flag:
        output_format = "json"
    elif mermaid_flag:
        output_format = "mermaid"
    elif reactlog_flag:
        output_format = "reactlog"
    elif html_out is not None:
        output_format = "html"

    sim_inputs: Dict[str, Any] = {}
    if inputs_json:
        try:
            parsed = json.loads(inputs_json)
            if isinstance(parsed, dict):
                typed_dict = cast(Dict[str, Any], parsed)
                sim_inputs.update(typed_dict)
        except Exception as e:
            if output_format == "json":
                click.echo(
                    json.dumps(
                        {"success": False, "error": f"Invalid JSON in --inputs: {e}"}
                    )
                )
            else:
                click.echo(cli_danger(f"Invalid JSON in --inputs: {e}"))
            sys.exit(1)

    for item in input_pairs:
        if "=" in item:
            k, v = item.split("=", 1)
            sim_inputs[k.strip()] = _parse_input_value(v.strip())
        else:
            sim_inputs[item.strip()] = True

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
                        click.echo(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": f"No Python files in directory: {path}",
                                }
                            )
                        )
                    else:
                        click.echo(
                            cli_danger(f"No Python files found in directory: {path}")
                        )
                    sys.exit(1)
        if not p.is_file():
            if output_format == "json":
                click.echo(
                    json.dumps({"success": False, "error": f"File not found: {path}"})
                )
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
                click.echo(
                    json.dumps(
                        {
                            "success": False,
                            "error": "No file specified and app.py not found in current directory.",
                        }
                    )
                )
            else:
                click.echo(
                    cli_danger(
                        "No file specified and app.py not found in current directory."
                    )
                )
            sys.exit(1)

    reactlog_data = generate_reactlog(
        source_code, inputs=sim_inputs if sim_inputs else None
    )

    if not reactlog_data.get("success"):
        if output_format == "json":
            click.echo(json.dumps(reactlog_data, indent=2))
        else:
            click.echo(
                cli_danger(
                    f"Failed to inspect reactive graph: {reactlog_data.get('error')}"
                )
            )
        sys.exit(1)

    if output_format == "html":
        out_file_path = html_out if html_out is not None else "reactlog.html"
        html_content = format_reactlog_html(
            reactlog_data, title=f"Reactlog: {target_desc}"
        )
        Path(out_file_path).write_text(html_content, encoding="utf-8")
        click.echo(
            cli_success(f"Interactive Reactlog HTML exported to {out_file_path}")
        )
        sys.exit(0)

    elif output_format == "json":
        reactlog_with_target = dict(reactlog_data)
        reactlog_with_target["target"] = target_desc
        click.echo(json.dumps(reactlog_with_target, indent=2))
        sys.exit(0)

    elif output_format == "mermaid":
        click.echo(format_graph_mermaid(reactlog_data))
        sys.exit(0)

    elif output_format == "dot":
        click.echo(format_graph_dot(reactlog_data))
        sys.exit(0)

    elif output_format == "reactlog":
        click.echo(cli_bold(f"Reactlog Execution Trace for {target_desc}"))
        click.echo(cli_info(str(reactlog_data["summary"])) + "\n")

        events = reactlog_data.get("events", [])
        click.echo(
            f"  {'Step':<6} {'Time':<9} {'Event':<14} {'Node':<24} {'Status':<12} {'Details'}"
        )
        click.echo("  " + "-" * 85)

        for ev in events:
            step_str = f"#{ev['step']}"
            time_str = f"+{ev['time_ms']}ms"
            ev_name = ev["event"]
            node_lbl = ev["node_label"] or "-"
            status = ev["status"]
            details = ev.get("details", "")

            status_styled = status
            if status == "ready":
                status_styled = click.style(status, fg="green")
            elif status == "dirty":
                status_styled = click.style(status, fg="yellow")
            elif status == "calculating":
                status_styled = click.style(status, fg="cyan")
            elif status == "error":
                status_styled = click.style(status, fg="red")

            click.echo(
                f"  {step_str:<6} {time_str:<9} {ev_name:<14} {node_lbl:<24} {status_styled:<21} {details}"
            )
        sys.exit(0)

    else:
        click.echo(cli_bold(f"Reactive Dependency Graph for {target_desc}"))
        click.echo(cli_info(str(reactlog_data["summary"])) + "\n")

        nodes_by_type: Dict[str, List[str]] = {
            "source": [],
            "conductor": [],
            "observer": [],
        }
        for n in reactlog_data.get("nodes", []):
            role: str = str(n.get("role", "conductor"))
            nodes_by_type.setdefault(role, []).append(str(n["id"]))

        if nodes_by_type["source"]:
            click.echo(cli_bold("Inputs (Sources):"))
            for inp in nodes_by_type["source"]:
                click.echo(f"  📥 input.{inp}")
            click.echo("")

        if nodes_by_type["conductor"]:
            click.echo(cli_bold("Reactive Calcs (Conductors):"))
            for c in nodes_by_type["conductor"]:
                click.echo(f"  ⚡ {c}")
            click.echo("")

        if nodes_by_type["observer"]:
            click.echo(cli_bold("Outputs & Effects (Observers):"))
            for out in nodes_by_type["observer"]:
                click.echo(f"  📊 {out}")
            click.echo("")

        edges = reactlog_data.get("edges", [])
        if edges:
            click.echo(cli_bold("Dependency Flow:"))
            for e in edges:
                click.echo(
                    f"  {cli_code(str(e['from']))}  \u27f6  {cli_bold(str(e['to']))}"
                )
        else:
            click.echo(cli_info("No direct reactive dependencies detected."))

        click.echo(
            cli_info(
                "\nTip: Run 'shiny inspect --reactlog' or 'shiny inspect --html' to see full time-travel execution."
            )
        )
        sys.exit(0)
