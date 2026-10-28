from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import _guide, main


def test_guide_list_all_topics() -> None:
    result = CliRunner().invoke(main, ["guide"])

    assert result.exit_code == 0
    assert "# Shiny for Python Guide Topics" in result.output
    assert "Foundations" in result.output
    assert "Dashboard building" in result.output
    assert "Testing & observability" in result.output
    assert "`reactivity`:" in result.output
    assert "`express`:" in result.output
    assert "`test-server`:" in result.output
    assert "`chat`:" in result.output


def test_guide_list_argument() -> None:
    result_none = CliRunner().invoke(main, ["guide"])
    result_list = CliRunner().invoke(main, ["guide", "list"])

    assert result_list.exit_code == 0
    assert result_list.output == result_none.output


def test_guide_show_topic_exact() -> None:
    result = CliRunner().invoke(main, ["guide", "reactivity"])

    assert result.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result.output
    assert "from shiny import reactive" in result.output


def test_guide_normalization() -> None:
    result_upper = CliRunner().invoke(main, ["guide", "REACTIVITY"])
    assert result_upper.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result_upper.output

    result_md = CliRunner().invoke(main, ["guide", "reactivity.md"])
    assert result_md.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result_md.output

    result_underscore = CliRunner().invoke(main, ["guide", "test_server"])
    assert result_underscore.exit_code == 0
    assert "test_server" in result_underscore.output


def test_guide_unknown_topic_reports_error_and_available() -> None:
    result = CliRunner().invoke(main, ["guide", "nonexistent-topic"])

    assert result.exit_code != 0
    assert "Unknown guide topic 'nonexistent-topic'" in result.output
    assert "Available topics:" in result.output
    assert "reactivity" in result.output


def test_guide_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_guide, "SKILLS_DIR", tmp_path / "nonexistent")

    result = CliRunner().invoke(main, ["guide"])

    assert result.exit_code != 0
    assert "No documentation or skills" in result.output
