from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

import click

from .._components import get_component_doc, list_components
from ._utils import cli_bold, cli_code, cli_danger, cli_info


@click.command(
    "docs",
    help="""Browse Shiny for Python components, signatures, docstrings, and snippets.

    List all components or view detailed documentation and usage snippets for a
    specific component or renderer.

    Examples:

        shiny docs
        shiny docs -c layout
        shiny docs ui.page_sidebar
        shiny docs render.data_frame --json
    """,
)
@click.argument("component", required=False, type=str)
@click.option(
    "-c",
    "--category",
    type=click.Choice(["layout", "cards", "inputs", "outputs", "renderers"], case_sensitive=False),
    default=None,
    help="Filter component list by category.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output documentation in JSON format.",
)
def docs(component: Optional[str], category: Optional[str], json_output: bool) -> None:
    if component is None:
        components = list_components(category)
        if json_output:
            click.echo(json.dumps({"components": components}, indent=2))
            sys.exit(0)

        header = f"Shiny for Python Components ({len(components)} total"
        if category:
            header += f" in '{category}'"
        header += ")\n"
        click.echo(cli_bold(header))

        cats: Dict[str, List[Dict[str, Any]]] = {}
        for item in components:
            cat: str = str(item.get("category", "other"))
            cats.setdefault(cat, []).append(item)

        for cat_name, items in sorted(cats.items()):
            click.echo(cli_bold(f"[{cat_name.upper()}]:"))
            for it in items:
                click.echo(f"  {cli_code(str(it['name'])):<32} {it.get('description', '')}")
            click.echo("")

        click.echo(cli_info("Run 'shiny docs <component_name>' for full signature and code snippets."))
        sys.exit(0)

    doc = get_component_doc(component)
    if doc is None:
        if json_output:
            click.echo(json.dumps({"error": f"Component '{component}' not found."}, indent=2))
        else:
            click.echo(cli_danger(f"Component '{component}' not found in Shiny component catalog."))
            click.echo(cli_info("Run 'shiny docs' to see all available components."))
        sys.exit(1)

    if json_output:
        click.echo(json.dumps(doc, indent=2))
        sys.exit(0)

    click.echo(cli_bold(f"{doc['name']}  ({doc.get('category', 'general')})\n"))
    click.echo(f"{doc.get('description', '')}\n")

    sig = doc.get("signature")
    if sig:
        click.echo(cli_bold("Signature:"))
        click.echo(f"  {doc['name']}{sig}\n")

    snippet = doc.get("snippet")
    if snippet:
        click.echo(cli_bold("Example Snippet:"))
        for line in snippet.splitlines():
            click.echo(f"  {line}")
        click.echo("")

    docstring = doc.get("docstring")
    if docstring:
        click.echo(cli_bold("Documentation:"))
        lines = [line.rstrip() for line in docstring.strip().splitlines()[:20]]
        for line in lines:
            click.echo(f"  {line}")
        if len(docstring.strip().splitlines()) > 20:
            click.echo("  ...")

    sys.exit(0)
