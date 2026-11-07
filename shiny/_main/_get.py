from __future__ import annotations

import re
from difflib import get_close_matches

import click

from ._skills import _find_skill

REFERENCE_LINK = re.compile(r"`references/([a-z0-9-]+)\.md`")
"""A backticked link to a reference file in a bundled skill."""


@click.group("get", help="Read documentation bundled with Shiny.")
def get() -> None:
    pass


@get.command(
    "skill",
    help="""Print a bundled Agent Skill or one of its references to stdout.

    Without --reference, print the skill's index. Use --reference to read one
    reference, for example: shiny get skill --name shiny-for-python --reference
    reactivity. Partial names and close spellings also work. If several
    references match, use an exact name from the reported matches.
    """,
)
@click.option(
    "--name", required=True, help="Name of the bundled skill. See 'shiny skills list'."
)
@click.option("--reference", help="Reference name, such as 'reactivity'.")
def get_skill(name: str, reference: str | None) -> None:
    skill_dir = _find_skill(name)
    document = skill_dir / "SKILL.md"
    if reference is not None:
        references = {
            path.stem: path
            for path in sorted((skill_dir / "references").glob("*.md"))
            if path.is_file()
        }
        if not references:
            raise click.ClickException(
                f"No references are bundled with skill {name!r}."
            )

        slug = (
            reference.strip()
            .lower()
            .removesuffix(".md")
            .replace("_", "-")
            .replace(" ", "-")
        )
        if slug not in references:
            matches = [candidate for candidate in references if slug in candidate]
            if not matches:
                matches = get_close_matches(
                    slug, possibilities=references, n=3, cutoff=0.6
                )
            if len(matches) > 1:
                raise click.ClickException(
                    f"Reference {reference!r} is ambiguous. Matches: {', '.join(matches)}.\n"
                    "Use an exact reference name."
                )
            if not matches:
                raise click.ClickException(
                    f"Unknown reference {reference!r}.\n"
                    f"Available references: {', '.join(references)}\n\n"
                    f"Run 'shiny get skill --name {name}' to read the skill's index."
                )
            slug = matches[0]
        document = references[slug]

    text = REFERENCE_LINK.sub(
        rf"`shiny get skill --name {name} --reference \1`",
        string=document.read_text(encoding="utf-8"),
    )
    click.echo(text, nl=False)
