from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .._validate import validate_shiny_code
from ._utils import cli_bold, cli_code, cli_danger, cli_info, cli_success, cli_warning


@click.command(
    "validate",
    help="""Perform static AST analysis and validation on Shiny for Python code.

    Validates Shiny apps against common reactivity errors, duplicate widget IDs,
    missing reactive call parentheses, and R Shiny idioms.

    Examples:

        shiny validate app.py
        shiny validate --code "from shiny.express import ui"
        shiny validate . --json
    """,
)
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option(
    "--code", type=str, default=None, help="Inline Python source code to validate."
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output validation report in JSON format.",
)
def validate(path: Optional[str], code: Optional[str], json_output: bool) -> None:
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
            app_file = p / "app.py"
            if app_file.is_file():
                p = app_file
            else:
                if json_output:
                    click.echo(
                        json.dumps(
                            {
                                "valid": False,
                                "error": f"Directory does not contain app.py: {path}",
                            }
                        )
                    )
                else:
                    click.echo(cli_danger(f"Directory does not contain app.py: {path}"))
                sys.exit(1)
        if not p.is_file():
            if json_output:
                click.echo(
                    json.dumps({"valid": False, "error": f"File not found: {path}"})
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
            if json_output:
                click.echo(
                    json.dumps(
                        {
                            "valid": False,
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
                click.echo(
                    "Usage: shiny validate <path_to_app.py> or shiny validate --code '...'"
                )
            sys.exit(1)

    result = validate_shiny_code(source_code)

    if json_output:
        result_with_target = dict(result)
        result_with_target["target"] = target_desc
        click.echo(json.dumps(result_with_target, indent=2))
        sys.exit(0 if result["valid"] else 1)

    click.echo(cli_bold(f"Validating {target_desc} (Mode: {result['mode']})\n"))

    if result["errors"]:
        click.echo(cli_bold("Errors:"))
        for err in result["errors"]:
            line_str = f"Line {err.get('line', '?')}"
            code_str = err.get("code", "")
            click.echo(
                f"  {cli_danger(line_str)}: {err['message']} ({cli_code(code_str)})"
            )
        click.echo("")

    if result["warnings"]:
        click.echo(cli_bold("Warnings:"))
        for warn in result["warnings"]:
            line_str = f"Line {warn.get('line', '?')}"
            code_str = warn.get("code", "")
            click.echo(
                f"  {cli_warning(line_str)}: {warn['message']} ({cli_code(code_str)})"
            )
        click.echo("")

    if result["valid"] and not result["warnings"]:
        click.echo(cli_success("All validation checks passed successfully!"))

    if (
        result["detected_inputs"]
        or result["detected_outputs"]
        or result["detected_reactives"]
    ):
        click.echo(cli_bold("\nDetected Reactive Structure:"))
        if result["detected_inputs"]:
            click.echo(
                f"  Inputs ({len(result['detected_inputs'])}): {', '.join(result['detected_inputs'])}"
            )
        if result["detected_reactives"]:
            click.echo(
                f"  Reactives ({len(result['detected_reactives'])}): {', '.join(result['detected_reactives'])}"
            )
        if result["detected_outputs"]:
            click.echo(
                f"  Outputs ({len(result['detected_outputs'])}): {', '.join(result['detected_outputs'])}"
            )

    if result["suggestions"]:
        click.echo(cli_bold("\nSuggestions:"))
        for s in result["suggestions"]:
            click.echo(f"  {cli_info(s)}")

    sys.exit(0 if result["valid"] else 1)
