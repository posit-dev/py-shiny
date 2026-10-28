from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import click

from ._skills import SKILLS_DIR

ROUTER_SKILL_NAME = "shiny-for-python"


class DocTopic(NamedTuple):
    category: str
    title: str
    description: str
    slug: str
    path: Path


def _parse_topics(skill_dir: Path) -> dict[str, DocTopic]:
    skill_md = skill_dir / "SKILL.md"
    references_dir = skill_dir / "references"
    if not skill_md.is_file() or not references_dir.is_dir():
        return {}

    topics: dict[str, DocTopic] = {}
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
                topics[clean_slug] = DocTopic(
                    category=current_category,
                    title=title.strip(),
                    description=desc.strip(),
                    slug=clean_slug,
                    path=ref_path,
                )

    for ref_file in sorted(references_dir.glob("*.md")):
        slug = ref_file.stem
        if slug not in topics:
            topics[slug] = DocTopic(
                category="Additional References",
                title=slug.replace("-", " ").title(),
                description="Reference documentation.",
                slug=slug,
                path=ref_file,
            )

    return topics


def _format_topic_list(topics: dict[str, DocTopic]) -> str:
    lines = [
        "# Shiny for Python Documentation Topics",
        "",
        "Use `shiny docs <topic>` to print full reference documentation to stdout.",
        "",
    ]
    categories: dict[str, list[DocTopic]] = {}
    for topic in topics.values():
        categories.setdefault(topic.category, []).append(topic)

    for category, cat_topics in categories.items():
        lines.append(f"### {category}")
        for t in cat_topics:
            lines.append(f"- `{t.slug}`: {t.description}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def show_docs(topic: str | None = None) -> None:
    skill_dir = SKILLS_DIR / ROUTER_SKILL_NAME
    if not skill_dir.is_dir():
        raise click.ClickException(
            "No documentation or skills are bundled in this installation of shiny."
        )

    topics = _parse_topics(skill_dir)
    if not topics:
        raise click.ClickException(
            "No documentation topics found in this installation of shiny."
        )

    cleaned_topic = topic.strip() if topic else ""
    if not cleaned_topic or cleaned_topic.lower() == "list":
        click.echo(_format_topic_list(topics), nl=False)
        return

    normalized_slug = cleaned_topic.lower().removesuffix(".md").replace("_", "-")
    doc_topic = topics.get(normalized_slug)
    if doc_topic is None:
        available = ", ".join(sorted(topics.keys()))
        raise click.ClickException(
            f"Unknown documentation topic {topic!r}.\n"
            f"Available topics: {available}\n\n"
            "Run 'shiny docs' without arguments to see all available topics."
        )

    click.echo(doc_topic.path.read_text(encoding="utf-8"))


@click.command(
    "docs",
    help="""View documentation topics and print reference docs to stdout.

    Run without arguments to list all available topics.
    Specify a topic name (e.g. `shiny docs reactivity`) to print its full reference guide.
    """,
)
@click.argument("topic", required=False, default=None)
def docs(topic: str | None = None) -> None:
    show_docs(topic=topic)
