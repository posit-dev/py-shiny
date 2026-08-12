"""Guard what the built wheel actually contains.

The packaging globs in ``pyproject.toml`` can go wrong in two directions, and
neither one fails the build:

* Files that *should* ship stop matching. Agent Skills live under
  ``shiny/.agents/skills/`` (the library-skills convention), and ``**`` in a
  setuptools package-data glob does not match hidden directories, so the
  ``.agents`` tree needs its own pattern. Drop it and the skills silently
  vanish from the wheel.
* Files that should *not* ship start matching. ``api-examples/`` trees are only
  read when building the docs, and every extra file costs deploy time on
  platforms that pay a per-file latency (posit-dev/py-shiny#2125).

So these tests build a real wheel and read its contents, rather than
reimplementing setuptools' glob matching -- a reimplementation only proves it
agrees with itself.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import cast

import pytest

REPO_ROOT = Path(__file__).parents[2]
PACKAGE_DIR = REPO_ROOT / "shiny"
SKILLS_DIR = PACKAGE_DIR / ".agents" / "skills"
ROUTER_SKILL_DIR = SKILLS_DIR / "shiny-for-python"

# Bounds on the number of files in the wheel, as a tripwire for packaging
# changes that add or drop files wholesale. As of #2435 the wheel holds ~975
# files. The ceiling keeps #2125 from regressing (before the `api-examples`
# exclusions the wheel held ~1490); the floor catches a broken include glob
# dropping an asset tree. Moving either bound is fine -- do it deliberately,
# after checking `sorted(Counter(n.split("/")[1] for n in names).items())` for
# what changed.
WHEEL_FILE_COUNT_MIN = 850
WHEEL_FILE_COUNT_MAX = 1100


@pytest.fixture(scope="session")
def wheel_names(tmp_path_factory: pytest.TempPathFactory) -> list[str]:
    """Names of every entry in a freshly built wheel."""
    build_root = tmp_path_factory.mktemp("wheel")
    src = build_root / "src"
    outdir = build_root / "dist"

    # Build from a copy rather than the repo itself: setuptools writes to a
    # `build/` directory beside the sources, so building in place both litters
    # the working tree and races when pytest-xdist runs this fixture in several
    # workers at once. `__pycache__` is copied along deliberately -- the wheel
    # must not pick it up, and that is one of the things under test.
    src.mkdir()
    shutil.copytree(PACKAGE_DIR, src / "shiny", symlinks=True)
    for name in ("pyproject.toml", "MANIFEST.in", "LICENSE", "README.md"):
        shutil.copyfile(REPO_ROOT / name, src / name)

    # Plant bytecode so `test_bytecode_is_not_shipped_in_the_wheel` has
    # something to catch. A real `__pycache__` only exists once something has
    # imported `shiny` from the source tree, which makes the guard fire or not
    # depending on what else ran first.
    pycache = src / "shiny" / "__pycache__"
    pycache.mkdir(exist_ok=True)
    (pycache / "_packaging_test_sentinel.cpython-000.pyc").write_bytes(b"")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from setuptools import build_meta; "
            "print(build_meta.build_wheel(sys.argv[1]))",
            str(outdir),
        ],
        cwd=src,
        capture_output=True,
        text=True,
        # The copy has no `.git`, so setuptools_scm cannot derive a version.
        # The value is irrelevant here; only the file list matters.
        env={**os.environ, "SETUPTOOLS_SCM_PRETEND_VERSION": "0.0.0"},
    )
    if result.returncode != 0:
        pytest.fail(f"Could not build the wheel:\n{result.stdout}\n{result.stderr}")

    wheels = list(outdir.glob("*.whl"))
    assert len(wheels) == 1, f"Expected exactly one wheel, got {wheels}"
    with zipfile.ZipFile(wheels[0]) as zf:
        return zf.namelist()


def shipped_files(wheel_names: list[str]) -> set[Path]:
    """Repo paths of the `shiny/...` files present in the wheel."""
    return {REPO_ROOT / name for name in wheel_names if name.startswith("shiny/")}


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())


def test_skills_directory_has_skills() -> None:
    assert SKILLS_DIR.is_dir()
    assert len(skill_dirs()) > 0


def test_every_skill_has_a_skill_md() -> None:
    for skill_dir in skill_dirs():
        assert (skill_dir / "SKILL.md").is_file(), f"{skill_dir} is missing SKILL.md"


def test_skill_files_are_shipped_in_the_wheel(wheel_names: list[str]) -> None:
    shipped = shipped_files(wheel_names)
    skill_files = [p for p in SKILLS_DIR.rglob("*") if p.is_file()]
    assert len(skill_files) > 0
    missing = sorted(
        str(p.relative_to(REPO_ROOT)) for p in skill_files if p not in shipped
    )
    assert not missing, (
        "Files under shiny/.agents/ are not matched by any "
        "[tool.setuptools.package-data] glob in pyproject.toml and were "
        f"silently dropped from the wheel: {missing}"
    )


def test_api_examples_are_not_shipped_in_the_wheel(wheel_names: list[str]) -> None:
    # `api-examples/` trees exist for `@add_example()` when building the docs.
    # Shipping them adds hundreds of files to the wheel, which slows down
    # deployments that pay a per-file cost. Every such tree must be excluded,
    # including nested ones like `shiny/experimental/api-examples/`, which the
    # top-level `api-examples/**` pattern does not reach.
    example_dirs = [p for p in PACKAGE_DIR.rglob("api-examples") if p.is_dir()]
    assert example_dirs, "no api-examples directories found -- did they move?"

    shipped = shipped_files(wheel_names)
    leaked = sorted(
        str(p.relative_to(REPO_ROOT))
        for d in example_dirs
        for p in d.rglob("*")
        if p.is_file() and p in shipped
    )
    assert not leaked, (
        f"{len(leaked)} api-examples files are not matched by any "
        "[tool.setuptools.exclude-package-data] pattern in pyproject.toml and "
        f"shipped in the wheel: {leaked[:10]}"
    )


def test_bytecode_is_not_shipped_in_the_wheel(wheel_names: list[str]) -> None:
    # The `shiny = ["**"]` package-data glob matches `__pycache__` too, so
    # without an exclusion the wheel's contents depend on whatever bytecode
    # happens to sit in the tree at build time -- hundreds of files, and a
    # different set on every machine.
    leaked = sorted(
        name
        for name in wheel_names
        if name.endswith(".pyc") or "/__pycache__/" in f"/{name}"
    )
    assert (
        not leaked
    ), f"{len(leaked)} compiled bytecode files shipped in the wheel: {leaked[:10]}"


def test_wheel_file_count_stays_within_bounds(wheel_names: list[str]) -> None:
    count = len(wheel_names)
    assert WHEEL_FILE_COUNT_MIN <= count <= WHEEL_FILE_COUNT_MAX, (
        f"The wheel holds {count} files, outside the expected range of "
        f"{WHEEL_FILE_COUNT_MIN}-{WHEEL_FILE_COUNT_MAX}. A packaging glob "
        "likely started matching a tree it should not (file count drives "
        "deploy time on platforms that pay a per-file latency) or stopped "
        "matching one it should. If the change is intended, update the bounds "
        "in this file."
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
    # Minimal SKILL.md frontmatter contract (agentskills.io specification).
    # Parse the frontmatter as real YAML (installers like library-skills use a
    # strict parser): a `: ` or other special sequence in an unquoted scalar is
    # invalid YAML and must fail here, not silently ship a skill that installers
    # cannot read.
    yaml = pytest.importorskip("yaml")
    for skill_dir in skill_dirs():
        text = (skill_dir / "SKILL.md").read_text()
        assert text.startswith("---\n"), f"{skill_dir}: SKILL.md missing frontmatter"
        frontmatter = text.split("---", 2)[1]
        try:
            loaded = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            raise AssertionError(
                f"{skill_dir}: SKILL.md frontmatter is not valid YAML: {e}"
            )
        assert isinstance(
            loaded, dict
        ), f"{skill_dir}: frontmatter is not a YAML mapping"
        data = cast("dict[str, object]", loaded)
        assert (
            data.get("name") == skill_dir.name
        ), f"{skill_dir}: frontmatter `name` must match its directory name"
        description = data.get("description")
        assert (
            isinstance(description, str) and description.strip()
        ), f"{skill_dir}: frontmatter is missing a non-empty `description`"
