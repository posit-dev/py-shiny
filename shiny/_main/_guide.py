from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import click

from ._skills import SKILLS_DIR

ROUTER_SKILL_NAME = "shiny-for-python"

REFERENCE_LINK = re.compile(r"`references/([a-z0-9-]+)\.md`")
"""A backticked link to a topic file, as written in the bundled skill."""


def as_cli_links(text: str) -> str:
    """Point topic links at `shiny guide <topic>` so stdout readers can follow them."""
    return REFERENCE_LINK.sub(r"`shiny guide \1`", text)


class GuideTopic(NamedTuple):
    category: str
    title: str
    description: str
    slug: str
    path: Path


def _parse_topics(skill_dir: Path) -> dict[str, GuideTopic]:
    skill_md = skill_dir / "SKILL.md"
    references_dir = skill_dir / "references"
    if not skill_md.is_file() or not references_dir.is_dir():
        return {}

    topics: dict[str, GuideTopic] = {}
    current_category = "General"
    row_pattern = re.compile(
        r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*`references/([^|]+?)\.md`\s*\|"
    )

    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_category = line[3:].strip()
            continue
        match = row_pattern.match(line)
        if match:
            title, desc, slug = match.groups()
            clean_slug = slug.strip()
            ref_path = references_dir / f"{clean_slug}.md"
            if ref_path.is_file():
                topics[clean_slug] = GuideTopic(
                    category=current_category,
                    title=title.strip(),
                    description=desc.strip(),
                    slug=clean_slug,
                    path=ref_path,
                )

    for ref_file in sorted(references_dir.glob("*.md")):
        slug = ref_file.stem
        if slug not in topics:
            topics[slug] = GuideTopic(
                category="Additional References",
                title=slug.replace("-", " ").title(),
                description="Reference documentation.",
                slug=slug,
                path=ref_file,
            )

    return topics


def _format_topic_list(topics: dict[str, GuideTopic]) -> str:
    lines = [
        "# Shiny for Python Guide Topics",
        "",
        "Use `shiny guide <topic>` to print full reference documentation to stdout.",
        "",
    ]
    categories: dict[str, list[GuideTopic]] = {}
    for topic in topics.values():
        categories.setdefault(topic.category, []).append(topic)

    for category, cat_topics in categories.items():
        lines.append(f"### {category}")
        for t in cat_topics:
            lines.append(f"- `{t.slug}`: {t.description}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def show_guide(topic: str | None = None) -> None:
    skill_dir = SKILLS_DIR / ROUTER_SKILL_NAME
    if not skill_dir.is_dir():
        raise click.ClickException(
            "No documentation or skills are bundled in this installation of shiny."
        )

    topics = _parse_topics(skill_dir)
    if not topics:
        raise click.ClickException(
            "No guide topics found in this installation of shiny."
        )

    cleaned_topic = topic.strip() if topic else ""
    if not cleaned_topic or cleaned_topic.lower() == "list":
        click.echo(_format_topic_list(topics), nl=False)
        return

    normalized_slug = cleaned_topic.lower().removesuffix(".md").replace("_", "-")
    guide_topic = topics.get(normalized_slug)
    if guide_topic is None:
        available = ", ".join(sorted(topics.keys()))
        raise click.ClickException(
            f"Unknown guide topic {topic!r}.\n"
            f"Available topics: {available}\n\n"
            "Run 'shiny guide' without arguments to see all available topics."
        )

    click.echo(as_cli_links(guide_topic.path.read_text(encoding="utf-8")))


@click.command(
    "guide",
    help="""Print a Shiny for Python guide topic to stdout, or list topics.

    Run without arguments to list all available topics.
    Specify a topic name (e.g. `shiny guide reactivity`) to print its full reference guide.
    """,
)
@click.argument("topic", required=False, default=None)
def guide(topic: str | None = None) -> None:
    show_guide(topic=topic)
