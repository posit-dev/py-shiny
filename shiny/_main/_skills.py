from __future__ import annotations

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
            value = line.removeprefix("description:").strip()
            # The description may be a quoted YAML scalar (required when it
            # contains a `: ` or other YAML-special sequence); unwrap it.
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
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
    help="""List and locate the Agent Skills bundled in the shiny package.

    Agent Skills are reference docs that teach coding agents how to use shiny's
    public APIs (debugging, testing, etc.). They ship inside the package under
    `shiny/.agents/skills/`.

    To make these skills available to your coding agent, install them with
    `library-skills` (https://library-skills.io), which symlinks the packaged
    skill into your project so it stays in sync when you upgrade shiny:

    \b
        uvx library-skills --claude   # Claude Code (installs into .claude/skills)
        uvx library-skills            # standard .agents/skills location

    (add `--copy` on Windows).
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
    print(
        "\nInstall these into your coding agent with `library-skills`:\n"
        "    uvx library-skills --claude   # Claude Code (.claude/skills)\n"
        "    uvx library-skills            # standard .agents/skills location\n"
        "See https://library-skills.io for details."
    )


@skills.command(
    "path",
    help="""Print the directory of a bundled Agent Skill.

    Use this to read a skill's `SKILL.md` and its supporting files
    (`references/`, `scripts/`, `assets/`) directly from the installed package.
    """,
)
@click.argument("name", type=str)
def skills_path(name: str) -> None:
    print(_find_skill(name))
