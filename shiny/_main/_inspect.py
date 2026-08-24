from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import click

from .._inspect import (
    format_graph_dot,
    format_graph_mermaid,
    format_reactlog_html,
    generate_reactlog,
    record_shiny_session,
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
    help="""Inspect and simulate the reactive dependency graph of a Shiny app.

    Analyzes reactive dependencies, visualizes dataflow graphs, records Playwright
    interactions with video capture, and generates interactive Reactlog reports.

    Examples:

        shiny inspect app.py
        shiny inspect app.py --record --video demo.webm --html reactlog.html
        shiny inspect app.py --format mermaid
        shiny inspect app.py --reactlog
        shiny inspect app.py --html
    """,
)
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option(
    "--code",
    type=str,
    default=None,
    help="Inline Python source code to inspect.",
)
@click.option(
    "--record",
    "record_flag",
    is_flag=True,
    default=False,
    help="Record user actions and browser video with Playwright, then generate a Reactlog.",
)
@click.option(
    "--video",
    "video_path",
    type=str,
    default="recording.webm",
    help="File path to save the recorded browser session video (default: recording.webm).",
)
@click.option(
    "--headless",
    is_flag=True,
    default=False,
    help="Run browser headlessly during Playwright recording.",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(
        ["text", "mermaid", "dot", "json", "html", "reactlog"], case_sensitive=False
    ),
    default="text",
    help="Output format for the dependency graph (default: text).",
)
@click.option(
    "--reactlog",
    "reactlog_flag",
    is_flag=True,
    default=False,
    help="Show step-by-step Reactlog event stream in terminal.",
)
@click.option(
    "--html",
    "html_out",
    type=str,
    is_flag=False,
    flag_value="reactlog.html",
    default=None,
    help="Export interactive HTML reactlog explorer (default: reactlog.html).",
)
@click.option(
    "--json",
    "json_flag",
    is_flag=True,
    default=False,
    help="Output reactive graph and Reactlog events as JSON.",
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
    help="JSON dictionary string of assumed values for dependency simulation.",
)
def inspect(
    path: Optional[str],
    code: Optional[str],
    record_flag: bool,
    video_path: str,
    headless: bool,
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
    elif html_out is not None or record_flag:
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
    app_file_to_run: Optional[str] = None
    temp_dir_to_clean: Optional[tempfile.TemporaryDirectory[str]] = None

    try:
        if code is not None:
            source_code = code
            target_desc = "<inline code>"
            if record_flag:
                temp_dir_to_clean = tempfile.TemporaryDirectory()
                temp_file = Path(temp_dir_to_clean.name) / "app.py"
                temp_file.write_text(code, encoding="utf-8")
                app_file_to_run = str(temp_file)
        elif path == "-":
            source_code = sys.stdin.read()
            target_desc = "<stdin>"
            if record_flag:
                temp_dir_to_clean = tempfile.TemporaryDirectory()
                temp_file = Path(temp_dir_to_clean.name) / "app.py"
                temp_file.write_text(source_code, encoding="utf-8")
                app_file_to_run = str(temp_file)
        elif path is not None:
            p = Path(path)
            if p.is_dir():
                candidate = p / "app.py"
                if candidate.is_file():
                    p = candidate
                else:
                    if output_format == "json":
                        click.echo(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": f"Directory does not contain app.py: {path}",
                                }
                            )
                        )
                    else:
                        click.echo(
                            cli_danger(f"Directory does not contain app.py: {path}")
                        )
                    sys.exit(1)
            if not p.is_file():
                if output_format == "json":
                    click.echo(
                        json.dumps(
                            {"success": False, "error": f"File not found: {path}"}
                        )
                    )
                else:
                    click.echo(cli_danger(f"File not found: {path}"))
                sys.exit(1)
            source_code = p.read_text(encoding="utf-8")
            target_desc = str(p)
            app_file_to_run = str(p)
        else:
            default_app = Path("app.py")
            if default_app.is_file():
                source_code = default_app.read_text(encoding="utf-8")
                target_desc = "app.py"
                app_file_to_run = "app.py"
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

        recorded_actions: Optional[List[Dict[str, Any]]] = None
        actual_video_path: Optional[str] = None

        if record_flag:
            if not app_file_to_run:
                if output_format == "json":
                    click.echo(
                        json.dumps(
                            {
                                "success": False,
                                "error": "Cannot record without an app file.",
                            }
                        )
                    )
                else:
                    click.echo(cli_danger("Cannot record without an app file."))
                sys.exit(1)

            is_machine_output = output_format in ("json", "mermaid", "dot")
            click.echo(
                cli_bold(f"Recording Playwright session for {target_desc}..."),
                err=is_machine_output,
            )
            rec_result = record_shiny_session(
                app_file_to_run,
                video_path=video_path,
                headless=headless,
            )
            if not rec_result.get("success"):
                err = rec_result.get("error", "Unknown error during recording")
                if output_format == "json":
                    click.echo(json.dumps({"success": False, "error": err}))
                else:
                    click.echo(cli_danger(f"Playwright recording failed: {err}"))
                sys.exit(1)

            raw_actions = rec_result.get("actions", [])
            recorded_actions = (
                cast(List[Dict[str, Any]], raw_actions)
                if isinstance(raw_actions, list)
                else []
            )
            actual_video_path = rec_result.get("video_path")
            act_count = len(recorded_actions)
            click.echo(
                cli_success(
                    f"Recorded {act_count} action(s) in {rec_result.get('duration_secs')}s"
                ),
                err=is_machine_output,
            )
            if actual_video_path:
                click.echo(
                    cli_info(f"Session video saved to: {actual_video_path}"),
                    err=is_machine_output,
                )

        reactlog_data = generate_reactlog(
            source_code,
            inputs=sim_inputs if sim_inputs else None,
            recorded_actions=recorded_actions,
            video_path=actual_video_path,
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
                reactlog_data,
                title=f"Reactive Log: {target_desc}",
                source_code=source_code,
                video_path=actual_video_path,
                html_path=out_file_path,
            )
            Path(out_file_path).write_text(html_content, encoding="utf-8")
            click.echo(
                cli_success(
                    f"Interactive reactive log explorer exported to {out_file_path}"
                )
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
            click.echo(cli_bold(f"Reactive Event Log for {target_desc}"))
            click.echo(cli_info(str(reactlog_data["summary"])) + "\n")

            events = reactlog_data.get("events", [])
            click.echo(
                f"  {'Step':<6} {'Event':<18} {'Node':<26} {'Status':<14} {'Details'}"
            )
            click.echo("  " + "-" * 88)

            for ev in events:
                step_str = f"#{ev['step']}"
                ev_name = ev["event"]
                node_lbl = ev["node_label"] or "-"
                status = ev["status"]
                details = ev.get("details", "")

                status_styled = status
                if status in ("assumed", "discovered"):
                    status_styled = click.style(status, fg="green")
                elif status == "affected":
                    status_styled = click.style(status, fg="yellow")
                elif status in ("ordering", "scheduled"):
                    status_styled = click.style(status, fg="cyan")
                elif status == "error":
                    status_styled = click.style(status, fg="red")

                click.echo(
                    f"  {step_str:<6} {ev_name:<18} {node_lbl:<26} {status_styled:<23} {details}"
                )
            sys.exit(0)

        else:
            click.echo(cli_bold(f"Reactive Dependency Graph for {target_desc}"))
            click.echo(cli_info(str(reactlog_data["summary"])) + "\n")

            nodes_by_type: Dict[str, List[Dict[str, Any]]] = {
                "source": [],
                "conductor": [],
                "observer": [],
            }
            for n in reactlog_data.get("nodes", []):
                role: str = str(n.get("role", "conductor"))
                nodes_by_type.setdefault(role, []).append(n)

            if nodes_by_type["source"]:
                click.echo(cli_bold("Inputs (Sources):"))
                for inp_node in nodes_by_type["source"]:
                    click.echo(f"  📥 {inp_node.get('label', inp_node['id'])}")
                click.echo("")

            if nodes_by_type["conductor"]:
                click.echo(cli_bold("Reactive Calcs (Conductors):"))
                for c_node in nodes_by_type["conductor"]:
                    click.echo(f"  ⚡ {c_node.get('label', c_node['id'])}")
                click.echo("")

            if nodes_by_type["observer"]:
                click.echo(cli_bold("Outputs & Effects (Observers):"))
                for out_node in nodes_by_type["observer"]:
                    click.echo(f"  📊 {out_node.get('label', out_node['id'])}")
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
                    "\nTip: Run 'shiny inspect --html' or 'shiny inspect --record' to explore the reactive log interactively."
                )
            )
            sys.exit(0)

    finally:
        if temp_dir_to_clean:
            try:
                temp_dir_to_clean.cleanup()
            except Exception:
                pass
