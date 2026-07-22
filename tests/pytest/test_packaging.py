"""Guard that bundled Agent Skills stay covered by the wheel packaging globs.

Agent Skills ship as package data under ``shiny/.agents/skills/`` (the
library-skills convention). Because ``**`` in setuptools package-data globs does
not match hidden directories, the ``.agents`` tree needs its own glob in
``pyproject.toml`` -- and nothing at build time fails if that glob is dropped,
the files just silently disappear from the wheel. These tests replicate
setuptools' matching (``glob.glob(os.path.join(src_dir, pattern),
recursive=True)`` in ``setuptools.command.build_py``) against the declared
patterns so a regression fails loudly here instead.
"""

from __future__ import annotations

import glob
import os
import re
from pathlib import Path

import pytest

tomllib = pytest.importorskip("tomllib")  # Stdlib in Python 3.11+

REPO_ROOT = Path(__file__).parents[2]
PACKAGE_DIR = REPO_ROOT / "shiny"
SKILLS_DIR = PACKAGE_DIR / ".agents" / "skills"
ROUTER_SKILL_DIR = SKILLS_DIR / "shiny-for-python"


def package_data_files() -> set[Path]:
    """Files shipped as `shiny` package data, per pyproject.toml globs."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    patterns: list[str] = pyproject["tool"]["setuptools"]["package-data"]["shiny"]

    matched: set[Path] = set()
    for pattern in patterns:
        for match in glob.glob(os.path.join(str(PACKAGE_DIR), pattern), recursive=True):
            if os.path.isfile(match):
                matched.add(Path(match))
    return matched


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())


def test_skills_directory_has_skills() -> None:
    assert SKILLS_DIR.is_dir()
    assert len(skill_dirs()) > 0


def test_every_skill_has_a_skill_md() -> None:
    for skill_dir in skill_dirs():
        assert (skill_dir / "SKILL.md").is_file(), f"{skill_dir} is missing SKILL.md"


def test_skill_files_are_covered_by_package_data_globs() -> None:
    shipped = package_data_files()
    skill_files = [p for p in SKILLS_DIR.rglob("*") if p.is_file()]
    assert len(skill_files) > 0
    missing = [p for p in skill_files if p not in shipped]
    assert not missing, (
        "Files under shiny/.agents/ are not matched by any "
        "[tool.setuptools.package-data] glob in pyproject.toml and would be "
        f"silently dropped from the wheel: {missing}"
    )


def test_router_skill_index_matches_reference_files() -> None:
    # The `shiny-for-python` skill is a router: its SKILL.md body indexes one
    # `references/<topic>.md` file per topic. Keep the index and the reference
    # files a 1:1 set so a new topic cannot be added to one without the other
    # (a dangling index link or an orphaned, unreachable reference).
    references_dir = ROUTER_SKILL_DIR / "references"
    assert references_dir.is_dir(), "shiny-for-python skill is missing references/"

    reference_files = {p.stem for p in references_dir.glob("*.md")}
    assert reference_files, "shiny-for-python/references/ has no .md files"

    skill_md = (ROUTER_SKILL_DIR / "SKILL.md").read_text()
    linked_topics = set(re.findall(r"references/([a-z0-9-]+)\.md", skill_md))

    dangling = linked_topics - reference_files
    assert not dangling, (
        "SKILL.md links to reference files that do not exist: " f"{sorted(dangling)}"
    )
    orphaned = reference_files - linked_topics
    assert not orphaned, (
        "references/ has files not linked from the SKILL.md index: "
        f"{sorted(orphaned)}"
    )


def test_skill_frontmatter_has_name_and_description() -> None:
    # Minimal SKILL.md frontmatter contract (agentskills.io specification);
    # also what `shiny skills list` will surface.
    for skill_dir in skill_dirs():
        text = (skill_dir / "SKILL.md").read_text()
        assert text.startswith("---\n"), f"{skill_dir}: SKILL.md missing frontmatter"
        frontmatter = text.split("---", 2)[1]
        assert (
            f"name: {skill_dir.name}" in frontmatter
        ), f"{skill_dir}: frontmatter `name` must match its directory name"
        assert (
            "description:" in frontmatter
        ), f"{skill_dir}: frontmatter is missing `description`"
