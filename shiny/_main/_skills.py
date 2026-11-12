from __future__ import annotations

import importlib.metadata
import json
import re
import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import cast

import click
from packaging.utils import canonicalize_name

SKILLS_DIR = Path(__file__).parent.parent / ".agents" / "skills"
REFERENCE_LINK = re.compile(r"`references/([a-z0-9-]+)\.md`")
NO_BUNDLED_SKILLS = "No skills are bundled in this installation of shiny."


@dataclass(frozen=True)
class DiscoveredSkill:
    name: str
    package: str
    path: Path
    description: str


def _available_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )


def _skill_description(skill_dir: Path) -> str:
    skill_file = skill_dir / "SKILL.md"
    try:
        if not skill_file.resolve().is_relative_to(skill_dir.resolve()):
            return ""
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""
    opening, _, rest = text.partition("\n")
    frontmatter, closing, _ = rest.partition("\n---\n")
    if opening != "---" or not closing:
        return ""
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            value = line.removeprefix("description:").strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return ""


def _is_shiny_ecosystem(package: str) -> bool:
    name = canonicalize_name(package)
    return name.startswith("shiny") or name in ("bslib", "htmltools")


def _entry_point_skills(target: object) -> Iterator[tuple[str, Path]]:
    if isinstance(target, (str, Path)):
        path = Path(target)
        if (path / "SKILL.md").is_file():
            yield path.name, path
        elif path.is_dir():
            for child in sorted(path.iterdir()):
                yield child.name, child
    elif isinstance(target, (list, tuple)):
        for item in cast("list[object] | tuple[object, ...]", target):
            if isinstance(item, (str, Path)):
                path = Path(item)
                yield path.name, path
    elif isinstance(target, dict):
        for name, value in cast(dict[object, object], target).items():
            if isinstance(name, str) and isinstance(value, (str, Path)):
                yield name, Path(value)


def _discover_skills(include_all: bool = False) -> dict[str, DiscoveredSkill]:
    skills: dict[str, DiscoveredSkill] = {}

    def add(name: str, package: str, path: Path) -> None:
        if len(name) > 64 or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is None:
            return
        if name not in skills and (path / "SKILL.md").is_file():
            skills[name] = DiscoveredSkill(
                name=name,
                package=package,
                path=path.absolute(),
                description=_skill_description(path),
            )

    for path in _available_skills():
        add(path.name, package="shiny", path=path)

    for ep in importlib.metadata.entry_points(group="shiny.skills"):
        package = ep.dist.name if ep.dist is not None else ep.name
        try:
            loaded: object = ep.load()
            target: object = loaded() if callable(loaded) else loaded
            for name, path in _entry_point_skills(target):
                add(name, package=package, path=path)
        except Exception as e:
            # An extension can import or run arbitrary code in its provider.
            click.echo(f"Could not load skills from {package}: {e}", err=True)

    distributions = [
        (dist.name, dist)
        for dist in importlib.metadata.distributions()
        if dist.name and canonicalize_name(dist.name) != "shiny"
    ]
    # Pick the same skill for list, get, path, and install even when names collide.
    distributions.sort(key=lambda item: (not _is_shiny_ecosystem(item[0]), item[0]))
    for package, dist in distributions:
        if not include_all and not _is_shiny_ecosystem(package):
            continue
        for file in dist.files or ():
            if file.name != "SKILL.md" or file.parts[-4:-2] != (".agents", "skills"):
                continue
            path = file.locate()
            if isinstance(path, Path):
                add(path.parent.name, package=package, path=path.parent)
    return skills


def _lookup_skill(name: str, skills: dict[str, DiscoveredSkill]) -> DiscoveredSkill:
    if not skills:
        raise click.ClickException("No skills found in this Python environment.")
    if name not in skills:
        available = ", ".join(sorted(skills))
        raise click.ClickException(
            f"Unknown skill {name!r}. Available skills: {available}"
        )
    return skills[name]


def _find_skill(name: str) -> Path:
    # Bundled lookups can skip loading third-party entry points.
    for path in _available_skills():
        if path.name == name:
            return path
    return _lookup_skill(name, skills=_discover_skills(include_all=True)).path


def _read_skill_document(name: str, reference: str | None) -> str:
    skill_dir = _find_skill(name)
    skill_dir = skill_dir.resolve()
    document = skill_dir / "SKILL.md"
    if reference is not None:
        references = {
            path.stem: path
            for path in sorted((skill_dir / "references").glob("*.md"))
            if path.is_file() and path.resolve().is_relative_to(skill_dir)
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

    try:
        if not document.resolve().is_relative_to(skill_dir):
            raise click.ClickException(f"Document is outside the skill: {document}")
        contents = document.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as e:
        raise click.ClickException(f"Could not read {document}: {e}") from e

    return REFERENCE_LINK.sub(
        rf"`shiny skill get {name} --reference \1`", string=contents
    )


def _install_skill(
    skill_info: DiscoveredSkill, target_dir: Path, *, copy: bool
) -> Path:
    dest = target_dir / skill_info.name
    try:
        source = skill_info.path.resolve()
        if not copy and dest.is_symlink() and dest.readlink() == source:
            return dest
        if dest.is_symlink() or dest.exists():
            raise FileExistsError(f"{dest} already exists")
        if target_dir.resolve().is_relative_to(source):
            raise click.ClickException(
                f"Cannot install a skill inside its source: {source}"
            )

        target_dir.mkdir(parents=True, exist_ok=True)
        if not copy:
            try:
                dest.symlink_to(source, target_is_directory=True)
            except FileExistsError:
                raise
            except OSError:
                # Some Windows setups restrict creating symlinks.
                pass
            else:
                return dest

        dest.mkdir()
        try:
            shutil.copytree(source, dest, symlinks=True, dirs_exist_ok=True)
        except OSError:
            shutil.rmtree(dest, ignore_errors=True)
            raise
    except OSError as e:
        raise click.ClickException(f"Could not install {skill_info.name!r}: {e}") from e
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
            click.echo("No skills found in this Python environment.")
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

    if name is not None and all_skills:
        raise click.UsageError("Specify either a skill name or --all.")
    discovered = _discover_skills(include_all=True)
    if not discovered:
        raise click.ClickException("No skills found to install.")

    target_dir = target
    if target_dir is None:
        target_dir = Path.cwd() / (".claude" if claude else ".agents") / "skills"
    selected = (
        [_lookup_skill(name, skills=discovered)]
        if name is not None
        else list(discovered.values())
    )
    for skill_info in selected:
        dest = _install_skill(skill_info, target_dir=target_dir, copy=copy)
        mode = "symlinked" if dest.is_symlink() else "copied"
        click.echo(f"Installed skill '{skill_info.name}' to {dest} ({mode})")


@click.group("skills", help="List and locate the Agent Skills bundled in Shiny.")
def skills() -> None:
    pass


@skills.command("list", help="List the bundled Agent Skills.")
def skills_list() -> None:
    skill_dirs = _available_skills()
    if not skill_dirs:
        click.echo(NO_BUNDLED_SKILLS)
        return
    width = max(len(path.name) for path in skill_dirs)
    for path in skill_dirs:
        click.echo(f"{path.name:<{width}}  {_skill_description(path)}")
    click.echo(
        "\nThese ship with the shiny package. To install them into your coding\n"
        "agent, run `library-skills` from your project directory:\n"
        "    uvx library-skills --claude   # Claude Code (.claude/skills)\n"
        "    uvx library-skills            # any other agent (.agents/skills)\n"
        "See https://library-skills.io for details."
    )


@skills.command("path", help="Print the directory of a bundled Agent Skill.")
@click.argument("name")
def skills_path(name: str) -> None:
    skill_dirs = _available_skills()
    if not skill_dirs:
        raise click.ClickException(NO_BUNDLED_SKILLS)
    for path in skill_dirs:
        if path.name == name:
            click.echo(path)
            return
    available = ", ".join(path.name for path in skill_dirs)
    raise click.ClickException(f"Unknown skill {name!r}. Available skills: {available}")
