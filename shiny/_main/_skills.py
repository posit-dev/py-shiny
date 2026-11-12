from __future__ import annotations

import importlib.metadata
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path

import click

SKILLS_DIR = Path(__file__).parent.parent / ".agents" / "skills"
REFERENCE_LINK = re.compile(r"`references/([a-z0-9-]+)\.md`")


@dataclass(frozen=True)
class DiscoveredSkill:
    name: str
    package: str
    path: Path
    description: str
    is_ecosystem: bool = False


def _available_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )


def _skill_description(skill_dir: Path) -> str:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return ""
    try:
        text = skill_file.read_text(encoding="utf-8")
    except OSError:
        return ""
    if not text.startswith("---\n"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    for line in parts[1].splitlines():
        if line.startswith("description:"):
            value = line.removeprefix("description:").strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return ""


def _is_shiny_ecosystem(pkg: str) -> bool:
    pkg_lower = pkg.lower()
    return "shiny" in pkg_lower or pkg_lower in ("bslib", "htmltools")


def _scan_skills_dir(
    skills_dir: Path,
    pkg: str,
    skills: dict[str, DiscoveredSkill],
    include_all: bool,
) -> None:
    is_eco = _is_shiny_ecosystem(pkg)
    if not include_all and not is_eco:
        return
    try:
        for s in skills_dir.iterdir():
            if s.is_dir() and (s / "SKILL.md").is_file() and s.name not in skills:
                skills[s.name] = DiscoveredSkill(
                    name=s.name,
                    package=pkg,
                    path=s,
                    description=_skill_description(s),
                    is_ecosystem=is_eco,
                )
    except OSError:
        pass


def _discover_skills(include_all: bool = False) -> dict[str, DiscoveredSkill]:
    skills: dict[str, DiscoveredSkill] = {}

    for p in _available_skills():
        skills[p.name] = DiscoveredSkill(
            name=p.name,
            package="shiny",
            path=p,
            description=_skill_description(p),
            is_ecosystem=True,
        )

    eps: list[importlib.metadata.EntryPoint] = []
    try:
        eps = list(importlib.metadata.entry_points(group="shiny.skills"))
    except Exception:
        eps = []

    for ep in eps:
        try:
            loaded = ep.load()
            target = loaded() if callable(loaded) else loaded
            pkg = getattr(ep.dist, "name", ep.name)
            if isinstance(target, (str, Path)):
                tpath = Path(target)
                if tpath.is_dir():
                    if (tpath / "SKILL.md").is_file() and tpath.name not in skills:
                        skills[tpath.name] = DiscoveredSkill(
                            name=tpath.name,
                            package=pkg,
                            path=tpath,
                            description=_skill_description(tpath),
                            is_ecosystem=True,
                        )
                    else:
                        for sub in tpath.iterdir():
                            if (
                                sub.is_dir()
                                and (sub / "SKILL.md").is_file()
                                and sub.name not in skills
                            ):
                                skills[sub.name] = DiscoveredSkill(
                                    name=sub.name,
                                    package=pkg,
                                    path=sub,
                                    description=_skill_description(sub),
                                    is_ecosystem=True,
                                )
            elif isinstance(target, (list, tuple)):
                for item in target:
                    ipath = Path(item)
                    if (
                        ipath.is_dir()
                        and (ipath / "SKILL.md").is_file()
                        and ipath.name not in skills
                    ):
                        skills[ipath.name] = DiscoveredSkill(
                            name=ipath.name,
                            package=pkg,
                            path=ipath,
                            description=_skill_description(ipath),
                            is_ecosystem=True,
                        )
            elif isinstance(target, dict):
                for sname, spath in target.items():
                    spath_obj = Path(spath)
                    if (
                        spath_obj.is_dir()
                        and (spath_obj / "SKILL.md").is_file()
                        and sname not in skills
                    ):
                        skills[sname] = DiscoveredSkill(
                            name=sname,
                            package=pkg,
                            path=spath_obj,
                            description=_skill_description(spath_obj),
                            is_ecosystem=True,
                        )
        except Exception:
            continue

    seen_entries: set[Path] = set()
    for entry in sys.path:
        try:
            entry_path = Path(entry).resolve()
        except OSError:
            continue
        if entry_path in seen_entries or not entry_path.is_dir():
            continue
        seen_entries.add(entry_path)

        try:
            for child in entry_path.iterdir():
                if not child.is_dir():
                    continue
                cname = child.name
                if (
                    cname == "shiny"
                    or cname.startswith(".")
                    or cname.endswith((".dist-info", ".egg-info", "__pycache__"))
                ):
                    continue
                child_skills = child / ".agents" / "skills"
                if child_skills.is_dir():
                    _scan_skills_dir(child_skills, cname, skills, include_all)
        except OSError:
            continue

    if not include_all:
        return {k: v for k, v in skills.items() if v.is_ecosystem}
    return skills


def _find_skill(name: str) -> Path:
    bundled = _available_skills()
    discovered = _discover_skills(include_all=True)
    if not bundled and not any(s.is_ecosystem for s in discovered.values()):
        raise click.ClickException(
            "No skills are bundled in this installation of shiny."
        )
    if name not in discovered:
        available = ", ".join(sorted(discovered.keys()))
        raise click.ClickException(
            f"Unknown skill {name!r}. Available skills: {available}"
        )
    return discovered[name].path


def _read_skill_document(name: str, reference: str | None) -> str:
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
                    f"Run 'shiny skill get {name}' to read the skill's index."
                )
            slug = matches[0]
        document = references[slug]

    return REFERENCE_LINK.sub(
        rf"`shiny skill get {name} --reference \1`",
        string=document.read_text(encoding="utf-8"),
    )


def install_skill(
    skill_name: str,
    target_dir: Path | str | None = None,
    claude: bool = False,
    copy: bool = False,
) -> Path:
    discovered = _discover_skills(include_all=True)
    if not discovered:
        raise click.ClickException("No skills found to install.")
    if skill_name not in discovered:
        available = ", ".join(sorted(discovered.keys()))
        raise click.ClickException(
            f"Unknown skill {skill_name!r}. Available skills: {available}"
        )
    skill_info = discovered[skill_name]

    if target_dir is not None:
        dest_base = Path(target_dir)
    elif claude:
        dest_base = Path.cwd() / ".claude" / "skills"
    else:
        dest_base = Path.cwd() / ".agents" / "skills"

    dest_base.mkdir(parents=True, exist_ok=True)
    dest = dest_base / skill_name

    if dest.is_symlink() or dest.exists():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()

    if copy:
        shutil.copytree(skill_info.path, dest)
    else:
        try:
            os.symlink(skill_info.path.resolve(), dest, target_is_directory=True)
        except OSError:
            shutil.copytree(skill_info.path, dest)
    return dest


@click.group(
    "skill",
    help="""List, inspect, and install Agent Skills for Shiny and extensions.

    Agent Skills teach coding agents how to use Shiny and extension APIs.
    They ship inside packages under `.agents/skills/`.
    """,
)
def skill() -> None:
    pass


@skill.command("list", help="List available Agent Skills.")
@click.option(
    "--all",
    "all_skills",
    is_flag=True,
    help="Include skills from all installed packages.",
)
@click.option("--json", "as_json", is_flag=True, help="Output skill list as JSON.")
def skill_list(all_skills: bool, as_json: bool) -> None:
    skills = _discover_skills(include_all=all_skills)
    if not skills:
        if as_json:
            click.echo("[]")
        else:
            click.echo("No skills are bundled in this installation of shiny.")
        return

    if as_json:
        data = [
            {
                "name": s.name,
                "package": s.package,
                "description": s.description,
                "path": str(s.path.resolve()),
            }
            for s in skills.values()
        ]
        click.echo(json.dumps(data, indent=2))
        return

    rows = [(f"[{s.package}] {s.name}", s.description) for s in skills.values()]
    width = max(len(col1) for col1, _ in rows)
    for col1, desc in rows:
        click.echo(f"{col1:<{width}}  {desc}")

    click.echo(
        "\nTo install a skill into your coding agent, run:\n"
        "    shiny skill install <name>\n"
        "    shiny skill install <name> --claude   # Claude Code (.claude/skills)\n"
        "\nOr use library-skills:\n"
        "    uvx library-skills --claude   # Claude Code (.claude/skills)\n"
        "    uvx library-skills            # any other agent (.agents/skills)\n"
        "See https://library-skills.io for details."
    )


@skill.command(
    "path",
    help="""Print the directory of an Agent Skill.

    Use this to read a skill's `SKILL.md` and its supporting files
    (`references/`, `scripts/`, `assets/`) directly from the installed package.
    """,
)
@click.argument("name", type=str)
def skill_path(name: str) -> None:
    click.echo(_find_skill(name))


@skill.command(
    "get",
    help="""Print an Agent Skill or one of its references to stdout.

    Without --reference, print the skill's index. Use --reference to read one
    reference, for example: shiny skill get shiny-for-python --reference
    reactivity. Partial names and close spellings also work.
    """,
)
@click.argument("name", required=False)
@click.option("--name", "name_opt", help="Name of the skill. See 'shiny skill list'.")
@click.option("--reference", help="Reference name, such as 'reactivity'.")
def skill_get(name: str | None, name_opt: str | None, reference: str | None) -> None:
    skill_name = name or name_opt
    if not skill_name:
        raise click.ClickException(
            "Missing required skill name. Usage: shiny skill get <name>"
        )
    click.echo(
        _read_skill_document(skill_name, reference),
        nl=False,
    )


@skill.command(
    "install",
    help="""Install one or all Agent Skills into the project.

    By default, symlinks the skill into `.agents/skills/<name>`.
    Use `--claude` to install into `.claude/skills/<name>` for Claude Code.
    Use `--copy` to copy files instead of symlinking.
    """,
)
@click.argument("name", required=False)
@click.option(
    "--all", "all_skills", is_flag=True, help="Install all discovered skills."
)
@click.option(
    "--claude",
    is_flag=True,
    help="Install into .claude/skills instead of .agents/skills.",
)
@click.option(
    "--target",
    type=click.Path(path_type=Path),
    help="Custom target directory for installation.",
)
@click.option(
    "--copy", is_flag=True, help="Copy the skill folder instead of creating a symlink."
)
def skill_install(
    name: str | None,
    all_skills: bool,
    claude: bool,
    target: Path | None,
    copy: bool,
) -> None:
    if not name and not all_skills:
        raise click.ClickException(
            "Please specify a skill name to install or use --all."
        )

    discovered = _discover_skills(include_all=True)
    if not discovered:
        raise click.ClickException("No skills found to install.")

    if all_skills:
        target_names = list(discovered.keys())
    else:
        assert name is not None
        target_names = [name]

    for target_name in target_names:
        dest = install_skill(
            target_name,
            target_dir=target,
            claude=claude,
            copy=copy,
        )
        mode = "copied" if copy or not dest.is_symlink() else "symlinked"
        click.echo(f"Installed skill '{target_name}' to {dest} ({mode})")


skills = click.Group(
    "skills",
    help=skill.help,
)
for cmd_name, cmd_obj in skill.commands.items():
    skills.add_command(cmd_obj, cmd_name)
