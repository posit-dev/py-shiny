from __future__ import annotations

import click

from .. import __version__
from ._create import create
from ._generate_test import add
from ._guide import guide
from ._quickstart import quickstart

# Re-exported as `shiny.run_app` (see `shiny/__init__.py`)
from ._run import run
from ._run import run_app as run_app  # noqa: F401
from ._skills import skills
from ._static import cells_to_app, get_shiny_deps, static, static_assets


@click.group("main", invoke_without_command=True)
@click.version_option(__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        click.echo(_command_listing(ctx))


def _command_listing(ctx: click.Context) -> str:
    """Every visible command with its full one-line help, for agents and humans."""
    rows: list[tuple[str, str]] = []
    for name in main.list_commands(ctx):
        command = main.get_command(ctx, name)
        if command is not None and not command.hidden:
            rows.append((name, command.get_short_help_str(limit=200)))
    width = max(len(name) for name, _ in rows)
    lines = ["Usage: shiny <COMMAND>", "", "Commands:"]
    lines.extend(f"  {name:<{width}}  {short_help}" for name, short_help in rows)
    return "\n".join(lines)


main.add_command(run)
main.add_command(add)
main.add_command(create)
main.add_command(guide)
main.add_command(quickstart)
main.add_command(skills)
main.add_command(static)
main.add_command(static_assets)
main.add_command(cells_to_app)
main.add_command(get_shiny_deps)
