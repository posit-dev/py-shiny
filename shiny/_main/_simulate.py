from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, cast

import click

from ..simulate import simulate_async
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
    "simulate",
    help="""Headlessly simulate a Shiny app in-memory without a browser.

    Initializes the reactive graph, injects input values, flushes reactivity,
    and captures rendered output values or runtime errors.

    Examples:

        shiny simulate app.py
        shiny simulate app.py -i n=25 -i region=North
        shiny simulate --code "..." --inputs '{"threshold": 100}' --json
    """,
)
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option(
    "--code", type=str, default=None, help="Inline Python source code to simulate."
)
@click.option(
    "-i",
    "--input",
    "input_pairs",
    multiple=True,
    help="Set an input value as KEY=VALUE (can be specified multiple times).",
)
@click.option(
    "--inputs",
    "inputs_json",
    type=str,
    default=None,
    help="JSON dictionary string of input values (e.g. '{\"n\": 25}').",
)
@click.option(
    "--timeout",
    "timeout_secs",
    type=float,
    default=3.0,
    help="Timeout in seconds for headless simulation (default: 3.0).",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output simulation results in JSON format.",
)
def simulate(
    path: Optional[str],
    code: Optional[str],
    input_pairs: tuple[str, ...],
    inputs_json: Optional[str],
    timeout_secs: float,
    json_output: bool,
) -> None:
    sim_inputs: Dict[str, Any] = {}

    if inputs_json:
        try:
            parsed = json.loads(inputs_json)
            if not isinstance(parsed, dict):
                raise ValueError(
                    f"JSON must be an object/dict, got {type(parsed).__name__}"
                )
            sim_inputs.update(cast(Dict[str, Any], parsed))
        except Exception as e:
            if json_output:
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

    app_path: Optional[str] = None
    if code is None:
        if path is not None:
            p = Path(path)
            if p.is_dir():
                candidate = p / "app.py"
                if candidate.is_file():
                    p = candidate
            if not p.is_file():
                if json_output:
                    click.echo(
                        json.dumps(
                            {"success": False, "error": f"File not found: {path}"}
                        )
                    )
                else:
                    click.echo(cli_danger(f"File not found: {path}"))
                sys.exit(1)
            app_path = str(p)
        else:
            default_app = Path("app.py")
            if default_app.is_file():
                app_path = str(default_app)
            else:
                if json_output:
                    click.echo(
                        json.dumps(
                            {
                                "success": False,
                                "error": "No app file specified and app.py not found in current directory.",
                            }
                        )
                    )
                else:
                    click.echo(
                        cli_danger(
                            "No app file specified and app.py not found in current directory."
                        )
                    )
                sys.exit(1)

    start_t = time.perf_counter()
    result = asyncio.run(
        simulate_async(
            code=code,
            file_path=app_path,
            inputs=sim_inputs,
            timeout_secs=timeout_secs,
            in_process=False,
        )
    )
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    if json_output:
        result_with_metrics = dict(result)
        result_with_metrics["elapsed_ms"] = round(elapsed_ms, 2)
        click.echo(json.dumps(result_with_metrics, indent=2, default=str))
        sys.exit(0 if result.get("success") else 1)

    target_name = app_path or "<inline code>"
    click.echo(cli_bold(f"Simulating {target_name} ({elapsed_ms:.1f}ms)\n"))

    if sim_inputs:
        click.echo(cli_bold("Simulated Inputs:"))
        for k, v in sim_inputs.items():
            click.echo(f"  {cli_code(k)} = {v!r}")
        click.echo("")

    if result.get("success"):
        click.echo(cli_success("Simulation completed successfully!\n"))
        outputs = result.get("outputs", {})
        if outputs:
            click.echo(cli_bold("Rendered Outputs:"))
            for out_name, out_val in outputs.items():
                val_repr = str(out_val).strip()
                if len(val_repr) > 120:
                    val_repr = val_repr[:117] + "..."
                click.echo(f"  {cli_bold(out_name)}: {val_repr}")
        else:
            click.echo(cli_info("No reactive outputs produced values."))

        exports = result.get("exports", {})
        if exports:
            click.echo(cli_bold("\nExported Test Values:"))
            for exp_name, exp_val in exports.items():
                click.echo(f"  {cli_bold(exp_name)}: {exp_val!r}")

        sys.exit(0)
    else:
        err_msg = result.get("error", "Unknown simulation error")
        click.echo(cli_danger(f"Simulation failed: {err_msg}\n"))

        errors = result.get("errors", {})
        if errors:
            click.echo(cli_bold("Reactive Errors:"))
            for out_name, err in errors.items():
                click.echo(f"  {cli_danger(out_name)}: {err}")

        tb = result.get("traceback")
        if tb:
            click.echo(cli_bold("\nTraceback:"))
            click.echo(tb)

        sys.exit(1)
