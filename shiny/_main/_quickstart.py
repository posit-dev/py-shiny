from __future__ import annotations

import click

from ._guide import ROUTER_SKILL_NAME, as_cli_links
from ._skills import SKILLS_DIR


@click.command(
    "quickstart",
    help="""Print the Shiny for Python agent skill to stdout.

    The skill is an index of topics. Each topic points to a `shiny guide <topic>`
    command that prints its full reference.
    """,
)
def quickstart() -> None:
    skill_md = SKILLS_DIR / ROUTER_SKILL_NAME / "SKILL.md"
    if not skill_md.is_file():
        raise click.ClickException(
            "No skills are bundled in this installation of shiny."
        )
    click.echo(as_cli_links(skill_md.read_text(encoding="utf-8")), nl=False)
