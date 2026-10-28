import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import _guide, _quickstart, main

SKILL_DIR = _guide.SKILLS_DIR / _guide.ROUTER_SKILL_NAME


def test_quickstart_prints_bundled_skill_with_cli_links() -> None:
    result = CliRunner().invoke(main, ["quickstart"])

    assert result.exit_code == 0
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert result.output == _guide.as_cli_links(skill_md)
    assert "references/" not in result.output


def test_quickstart_guide_commands_all_resolve() -> None:
    result = CliRunner().invoke(main, ["quickstart"])

    linked = set(re.findall(r"`shiny guide ([a-z0-9-]+)`", result.output))
    topics = set(_guide._parse_topics(SKILL_DIR))
    assert linked == topics


def test_quickstart_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_quickstart, "SKILLS_DIR", tmp_path / "nonexistent")

    result = CliRunner().invoke(main, ["quickstart"])

    assert result.exit_code != 0
    assert "No skills" in result.output


def test_bare_shiny_lists_every_command_untruncated() -> None:
    result = CliRunner().invoke(main, [])

    assert result.exit_code == 0
    assert result.output.startswith("Usage: shiny <COMMAND>\n")
    assert "..." not in result.output
    for name in main.list_commands(main.make_context("shiny", [])):
        assert re.search(rf"^  {re.escape(name)}\s", result.output, re.MULTILINE)
