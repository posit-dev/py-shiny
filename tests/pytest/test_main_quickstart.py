import re
import textwrap

import pytest
from click.testing import CliRunner

from shiny import __version__
from shiny._main import _quickstart, main


def test_quickstart_prints_a_one_screen_welcome() -> None:
    result = CliRunner().invoke(main, args=["quickstart"])

    assert result.exit_code == 0
    assert result.output.startswith(f"# Welcome to Shiny for Python {__version__}\n")
    assert "uv init myapp" in result.output
    assert "uv add shiny" in result.output
    assert "uvx library-skills" in result.output
    assert "--claude" in result.output
    assert "https://shiny.posit.co/py/get-started/" in result.output
    assert "https://shiny.posit.co/py/docs/overview.html" in result.output
    assert (
        sum(
            max(1, len(textwrap.wrap(line, width=80)))
            for line in result.output.splitlines()
        )
        <= 24
    )


def test_quickstart_points_to_the_bundled_skill() -> None:
    result = CliRunner().invoke(main, args=["quickstart"])

    assert "`uv run shiny skills path shiny-for-python`" in result.output
    assert "SKILL.md" in result.output
    assert "name: shiny-for-python" not in result.output
    assert "| Topic |" not in result.output

    skill_path = CliRunner().invoke(main, args=["skills", "path", "shiny-for-python"])
    assert skill_path.exit_code == 0


@pytest.mark.parametrize(
    ("version", "ref"),
    argvalues=[("1.9.0", "v1.9.0"), ("1.9.0rc1", "v1.9.0rc1"), ("1.9.1.dev2", "main")],
)
def test_quickstart_links_to_the_installed_versions_changes(
    monkeypatch: pytest.MonkeyPatch, version: str, ref: str
) -> None:
    monkeypatch.setattr(_quickstart, name="__version__", value=version)

    result = CliRunner().invoke(main, args=["quickstart"])

    assert result.exit_code == 0
    assert f"What's new in {version}" in result.output
    assert (
        f"https://github.com/posit-dev/py-shiny/blob/{ref}/CHANGELOG.md"
        in result.output
    )


def test_bare_shiny_lists_every_command_untruncated() -> None:
    result = CliRunner().invoke(main, [])

    assert result.exit_code == 0
    assert result.output.startswith("Usage: shiny <COMMAND>\n")
    assert "..." not in result.output
    for name in main.list_commands(main.make_context("shiny", [])):
        assert re.search(rf"^  {re.escape(name)}\s", result.output, re.MULTILINE)
