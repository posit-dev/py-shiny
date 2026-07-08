from __future__ import annotations

import sys
from pathlib import Path

import click

SKILLS_DIR = Path(__file__).parent.parent / ".agents" / "skills"
"""Location of the Agent Skills bundled in the shiny package."""


def _available_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )


def _skill_description(skill_dir: Path) -> str:
    """Extract the one-line `description:` from a SKILL.md's YAML frontmatter."""
    text = (skill_dir / "SKILL.md").read_text()
    if not text.startswith("---\n"):
        return ""
    frontmatter = text.split("---", 2)[1]
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            return line.removeprefix("description:").strip()
    return ""


def _find_skill(name: str) -> Path:
    """Return the directory of the named skill, or raise a helpful error."""
    skill_dirs = _available_skills()
    if not skill_dirs:
        raise click.ClickException(
            "No skills are bundled in this installation of shiny."
        )
    skill_dir = next((p for p in skill_dirs if p.name == name), None)
    if skill_dir is None:
        available = ", ".join(p.name for p in skill_dirs)
        raise click.ClickException(
            f"Unknown skill {name!r}. Available skills: {available}"
        )
    return skill_dir


@click.group(
    "skills",
    help="""List and read the Agent Skills bundled in the shiny package.

    Agent Skills are reference docs that teach coding agents how to use shiny's
    public APIs (debugging, testing, etc.). They ship inside the package under
    `shiny/.agents/skills/`.
    """,
)
def skills() -> None:
    pass


@skills.command("list", help="List the bundled Agent Skills.")
def skills_list() -> None:
    skill_dirs = _available_skills()
    if not skill_dirs:
        print("No skills are bundled in this installation of shiny.")
        return
    width = max(len(p.name) for p in skill_dirs)
    for skill_dir in skill_dirs:
        print(f"{skill_dir.name:<{width}}  {_skill_description(skill_dir)}")


@skills.command("get", help="Print a bundled Agent Skill's SKILL.md to stdout.")
@click.argument("name", type=str)
def skills_get(name: str) -> None:
    sys.stdout.write((_find_skill(name) / "SKILL.md").read_text())


@skills.command(
    "path",
    help="""Print the directory of a bundled Agent Skill.

    Use this to read a skill's supporting files (`references/`, `scripts/`,
    `assets/`) directly from the installed package.
    """,
)
@click.argument("name", type=str)
def skills_path(name: str) -> None:
    print(_find_skill(name))
