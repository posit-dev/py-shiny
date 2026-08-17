from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .._components import TEMPLATE_CATALOG, get_template
from ._utils import cli_bold, cli_code, cli_danger, cli_info, cli_success


@click.command(
    "scaffold",
    help="""Generate starter code and templates for Shiny for Python apps.

    Print starter template code to stdout or write directly to a destination file.

    Examples:

        shiny scaffold --list
        shiny scaffold express_dashboard
        shiny scaffold core_dashboard -o app.py
        shiny scaffold ai_chat --json
    """,
)
@click.argument("template", required=False, type=str)
@click.option("-o", "--out", "out_path", type=click.Path(), default=None, help="Write generated template directly to this file path.")
@click.option("-l", "--list", "list_flag", is_flag=True, default=False, help="List all available starter templates.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Output template data in JSON format.")
def scaffold(template: Optional[str], out_path: Optional[str], list_flag: bool, json_output: bool) -> None:
    if list_flag or template is None:
        templates = list(TEMPLATE_CATALOG.values())
        if json_output:
            click.echo(json.dumps({"templates": templates}, indent=2))
            sys.exit(0)

        click.echo(cli_bold("Available Shiny Starter Templates:\n"))
        for t in templates:
            click.echo(f"  {cli_code(t['name']):<24} {t.get('description', '')}")
        click.echo(cli_info("\nRun 'shiny scaffold <template_name> [-o app.py]' to generate a template."))
        sys.exit(0)

    tmpl = get_template(template)
    if tmpl is None:
        if json_output:
            click.echo(json.dumps({"error": f"Template '{template}' not found."}, indent=2))
        else:
            click.echo(cli_danger(f"Template '{template}' not found."))
            click.echo(cli_info("Run 'shiny scaffold --list' to view available templates."))
        sys.exit(1)

    if json_output:
        click.echo(json.dumps(tmpl, indent=2))
        sys.exit(0)

    if out_path:
        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(tmpl["code"], encoding="utf-8")
        click.echo(cli_success(f"Scaffolded '{template}' template to {out_path}"))
        sys.exit(0)

    click.echo(tmpl["code"])
    sys.exit(0)
