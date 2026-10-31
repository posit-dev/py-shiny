from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .._validate import (
    _CLEAN_MESSAGE,
    ValidationRuleLike,
    installed_validation_rules,
    load_validation_rule,
    validate_shiny_code,
    validate_shiny_file,
)
from ._utils import cli_bold, cli_code, cli_danger, cli_info, cli_success, cli_warning


@click.command(
    "validate",
    help="""Check Shiny for Python code for reactivity mistakes without running it.

    Reports Shiny-specific problems only: inputs, values, or calcs read outside
    a reactive context, reads inside extended tasks, uncalled inputs, assignment
    to inputs, multiple render decorators, reactive.event in the wrong decorator
    position, duplicate input/output IDs, UI outputs without a renderer (and
    the reverse), effects that return a value or re-trigger themselves, calcs
    with side effects, mutating an object held by a reactive value, and handlers
    that swallow extended-task errors. Syntax, import, name, and attribute
    errors are left to your type checker or linter. File targets also check
    local Python imports within the app directory without executing them.
    Exits with status 1 when errors are found. Warnings are reported but exit 0
    unless --strict is passed.

    Examples:

        shiny validate app.py
        shiny validate app.py --strict
        shiny validate --code "from shiny.express import ui"
        shiny validate . --json
        shiny validate app.py --validator my_rules:NoPrintRule
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
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with status 1 on warnings as well as errors.",
)
@click.option(
    "--validator",
    "validator_specs",
    multiple=True,
    metavar="MODULE:ATTR",
    help="Extra validation rule (ValidationRule subclass or callable). Repeatable; "
    "runs alongside rules installed under the 'shiny.validators' entry-point group.",
)
def validate(
    path: Optional[str],
    code: Optional[str],
    json_output: bool,
    strict: bool,
    validator_specs: tuple[str, ...],
) -> None:
    extra_rules: list[ValidationRuleLike] = []
    for spec in validator_specs:
        try:
            extra_rules.append(load_validation_rule(spec))
        except Exception as e:
            raise click.BadParameter(
                f"{spec}: {type(e).__name__}: {e}", param_hint="'--validator'"
            ) from e

    source_code: str = ""
    target_desc: str = ""
    source_path: Path | None = None

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
        source_path = p
        target_desc = str(p)
    else:
        default_app = Path("app.py")
        if default_app.is_file():
            source_path = default_app
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

    rules = [*installed_validation_rules(), *extra_rules]
    result = (
        validate_shiny_file(source_path, rules=rules)
        if source_path is not None
        else validate_shiny_code(source_code, rules=rules)
    )

    exit_code = 0 if (result.clean if strict else result.valid) else 1

    if json_output:
        result_with_target = dict(result.to_dict())
        result_with_target["target"] = target_desc
        click.echo(json.dumps(result_with_target, indent=2))
        sys.exit(exit_code)

    click.echo(cli_bold(f"Validating {target_desc} (Mode: {result.mode})\n"))

    if result.errors:
        click.echo(cli_bold("Errors:"))
        for err in result.errors:
            line_str = (
                f"{err['file']}:{err['line']}"
                if "file" in err
                else f"Line {err['line']}"
            )
            code_str = err["code"]
            click.echo(
                f"  {cli_danger(line_str)}: {err['message']} ({cli_code(code_str)})"
            )
        click.echo("")

    if result.warnings:
        click.echo(cli_bold("Warnings:"))
        for warn in result.warnings:
            line_str = (
                f"{warn['file']}:{warn['line']}"
                if "file" in warn
                else f"Line {warn['line']}"
            )
            code_str = warn["code"]
            click.echo(
                f"  {cli_warning(line_str)}: {warn['message']} ({cli_code(code_str)})"
            )
        click.echo("")

    if result.clean:
        click.echo(cli_success(_CLEAN_MESSAGE))
    elif result.valid:
        n = len(result.warnings)
        click.echo(cli_warning(f"No errors found ({n} warning{'s' * (n != 1)})."))

    if result.detected_inputs or result.detected_outputs or result.detected_reactives:
        click.echo(cli_bold("\nDetected Reactive Structure:"))
        if result.detected_inputs:
            click.echo(
                f"  Inputs ({len(result.detected_inputs)}): {', '.join(result.detected_inputs)}"
            )
        if result.detected_reactives:
            click.echo(
                f"  Reactives ({len(result.detected_reactives)}): {', '.join(result.detected_reactives)}"
            )
        if result.detected_outputs:
            click.echo(
                f"  Outputs ({len(result.detected_outputs)}): {', '.join(result.detected_outputs)}"
            )

    if result.suggestions:
        click.echo(cli_bold("\nSuggestions:"))
        for s in result.suggestions:
            click.echo(f"  {cli_info(s)}")

    sys.exit(exit_code)
