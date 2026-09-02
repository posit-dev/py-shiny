import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import _skills as _main_skills
from shiny._main import main

SKILLS_DIR = Path(_main_skills.__file__).parent.parent / ".agents" / "skills"

# The shiny package ships a single bundled skill, `shiny-for-python`, whose
# SKILL.md is a routing index into per-topic `references/` files.
SKILL_NAME = "shiny-for-python"


@pytest.mark.parametrize("skill_name", ["shiny-for-python", "shiny-doctor"])
def test_skills_list_shows_names_and_descriptions(skill_name: str) -> None:
    result = CliRunner().invoke(main, ["skills", "list"])

    assert result.exit_code == 0
    assert skill_name in result.output
    skill_line = next(line for line in result.output.splitlines() if skill_name in line)
    skill_md = (SKILLS_DIR / skill_name / "SKILL.md").read_text()
    match = re.search(r'^description: "?(.+?)"?$', skill_md, re.MULTILINE)
    assert match is not None
    assert match.group(1)[:40] in skill_line


def test_skills_list_with_empty_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_main_skills, "SKILLS_DIR", tmp_path)

    result = CliRunner().invoke(main, ["skills", "list"])

    assert result.exit_code == 0
    assert "No skills" in result.output


@pytest.mark.parametrize("skill_name", ["shiny-for-python", "shiny-doctor"])
def test_skills_path_prints_skill_directory(skill_name: str) -> None:
    result = CliRunner().invoke(main, ["skills", "path", skill_name])

    assert result.exit_code == 0
    assert result.output == f"{SKILLS_DIR / skill_name}\n"
    assert Path(result.output.strip()).is_absolute()


def test_skills_path_unknown_name_lists_available_skills() -> None:
    result = CliRunner().invoke(main, ["skills", "path", "does-not-exist"])

    assert result.exit_code != 0
    assert "does-not-exist" in result.output
    assert "shiny-for-python" in result.output
    assert "shiny-doctor" in result.output


def test_skills_path_with_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_main_skills, "SKILLS_DIR", tmp_path / "nope")

    result = CliRunner().invoke(main, ["skills", "path", SKILL_NAME])

    assert result.exit_code != 0
    assert "No skills" in result.output
