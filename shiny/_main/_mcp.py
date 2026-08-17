from __future__ import annotations

import json

import click

from .. import __version__
from ..mcp._prompts import list_mcp_prompts
from ..mcp._resources import list_mcp_resources
from ..mcp._server import run_server
from ..mcp._tools import get_mcp_tools_definitions


@click.group(
    "mcp",
    invoke_without_command=True,
    help="""Model Context Protocol (MCP) server for Shiny for Python.

    Provides AI coding assistants (Claude Desktop, Cursor, Copilot, etc.) with
    validation, headless simulation, component discovery, and documentation tools.

    To start the MCP server over stdio, run:
        shiny mcp
    """,
)
@click.pass_context
def mcp(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        run_server()


@mcp.command("run", help="Run the Shiny MCP server over stdio.")
def mcp_run() -> None:
    run_server()


@mcp.command("info", help="Display Shiny MCP server capabilities and configuration.")
def mcp_info() -> None:
    tools = get_mcp_tools_definitions()
    resources = list_mcp_resources()
    prompts = list_mcp_prompts()

    click.echo(f"Shiny for Python MCP Server v{__version__}\n")
    click.echo(f"Tools ({len(tools)}):")
    for t in tools:
        click.echo(f"  - {t['name']}: {t['description']}")

    click.echo(f"\nResources ({len(resources)}):")
    for r in resources:
        click.echo(f"  - {r['uri']}: {r['name']}")

    click.echo(f"\nPrompts ({len(prompts)}):")
    for p in prompts:
        click.echo(f"  - {p['name']}: {p['description']}")

    config_example = {
        "mcpServers": {
            "shiny": {
                "command": "shiny",
                "args": ["mcp"],
            }
        }
    }
    click.echo(
        "\nExample MCP Client Configuration (claude_desktop_config.json / settings.json):"
    )
    click.echo(json.dumps(config_example, indent=2))
