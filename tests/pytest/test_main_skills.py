from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny import _main_skills
from shiny._main import main

SKILLS_DIR = Path(_main_skills.__file__).parent / ".agents" / "skills"


def test_skills_list_shows_names_and_descriptions() -> None:
    result = CliRunner().invoke(main, ["skills", "list"])

    assert result.exit_code == 0
    assert "debugging" in result.output
    # The one-line description from the skill's frontmatter is shown
    debugging_line = next(
        line for line in result.output.splitlines() if "debugging" in line
    )
    assert "test mode" in debugging_line or "debugging a Shiny" in debugging_line


def test_skills_get_prints_skill_md() -> None:
    result = CliRunner().invoke(main, ["skills", "get", "debugging"])

    assert result.exit_code == 0
    expected = (SKILLS_DIR / "debugging" / "SKILL.md").read_text()
    assert result.output == expected


def test_skills_get_unknown_name_lists_available_skills() -> None:
    result = CliRunner().invoke(main, ["skills", "get", "does-not-exist"])

    assert result.exit_code != 0
    assert "does-not-exist" in result.output
    assert "debugging" in result.output


def test_skills_path_prints_skill_directory() -> None:
    result = CliRunner().invoke(main, ["skills", "path", "debugging"])

    assert result.exit_code == 0
    assert result.output == f"{SKILLS_DIR / 'debugging'}\n"
    assert Path(result.output.strip()).is_absolute()


def test_skills_path_unknown_name_lists_available_skills() -> None:
    result = CliRunner().invoke(main, ["skills", "path", "does-not-exist"])

    assert result.exit_code != 0
    assert "does-not-exist" in result.output
    assert "debugging" in result.output


def test_skills_list_with_empty_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_main_skills, "SKILLS_DIR", tmp_path)

    result = CliRunner().invoke(main, ["skills", "list"])

    assert result.exit_code == 0
    assert "No skills" in result.output


def test_skills_get_with_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_main_skills, "SKILLS_DIR", tmp_path / "nope")

    result = CliRunner().invoke(main, ["skills", "get", "debugging"])

    assert result.exit_code != 0
    assert "No skills" in result.output
