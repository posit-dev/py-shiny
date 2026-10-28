from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import _docs, main


def test_docs_list_all_topics() -> None:
    result = CliRunner().invoke(main, ["docs"])

    assert result.exit_code == 0
    assert "# Shiny for Python Documentation Topics" in result.output
    assert "Foundations" in result.output
    assert "Dashboard building" in result.output
    assert "Testing & observability" in result.output
    assert "`reactivity`:" in result.output
    assert "`express`:" in result.output
    assert "`test-server`:" in result.output
    assert "`chat`:" in result.output


def test_docs_list_argument() -> None:
    result_none = CliRunner().invoke(main, ["docs"])
    result_list = CliRunner().invoke(main, ["docs", "list"])

    assert result_list.exit_code == 0
    assert result_list.output == result_none.output


def test_docs_show_topic_exact() -> None:
    result = CliRunner().invoke(main, ["docs", "reactivity"])

    assert result.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result.output
    assert "from shiny import reactive" in result.output


def test_docs_normalization() -> None:
    result_upper = CliRunner().invoke(main, ["docs", "REACTIVITY"])
    assert result_upper.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result_upper.output

    result_md = CliRunner().invoke(main, ["docs", "reactivity.md"])
    assert result_md.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result_md.output

    result_underscore = CliRunner().invoke(main, ["docs", "test_server"])
    assert result_underscore.exit_code == 0
    assert "test_server" in result_underscore.output


def test_docs_unknown_topic_reports_error_and_available() -> None:
    result = CliRunner().invoke(main, ["docs", "nonexistent-topic"])

    assert result.exit_code != 0
    assert "Unknown documentation topic 'nonexistent-topic'" in result.output
    assert "Available topics:" in result.output
    assert "reactivity" in result.output


def test_docs_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_docs, "SKILLS_DIR", tmp_path / "nonexistent")

    result = CliRunner().invoke(main, ["docs"])

    assert result.exit_code != 0
    assert "No documentation or skills" in result.output
