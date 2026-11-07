import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import _skills, main


def test_get_skill_prints_index_with_reference_commands() -> None:
    result = CliRunner().invoke(
        main, args=["get", "skill", "--name", "shiny-for-python"]
    )

    assert result.exit_code == 0
    assert "name: shiny-for-python" in result.output
    assert "# Shiny for Python" in result.output
    assert (
        "`shiny get skill --name shiny-for-python --reference reactivity`"
        in result.output
    )
    assert "references/" not in result.output


def test_get_skill_reference_commands_all_resolve() -> None:
    result = CliRunner().invoke(
        main, args=["get", "skill", "--name", "shiny-for-python"]
    )
    references = re.findall(
        r"`shiny get skill --name shiny-for-python --reference ([a-z0-9-]+)`",
        string=result.output,
    )

    assert references
    for reference in references:
        result = CliRunner().invoke(
            main,
            args=[
                "get",
                "skill",
                "--name",
                "shiny-for-python",
                "--reference",
                reference,
            ],
        )
        assert result.exit_code == 0, reference
        assert result.output.strip()


@pytest.mark.parametrize(
    "reference",
    argvalues=["reactivity", "REACTIVITY", "reactivity.md", "reactive", "reactivty"],
)
def test_get_skill_reference_accepts_close_names(reference: str) -> None:
    result = CliRunner().invoke(
        main,
        args=["get", "skill", "--name", "shiny-for-python", "--reference", reference],
    )

    assert result.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result.output
    assert "from shiny import reactive" in result.output
    assert (
        "`shiny get skill --name shiny-for-python --reference extended-tasks`"
        in result.output
    )
    assert "references/" not in result.output


@pytest.mark.parametrize(
    "reference", argvalues=["test_server", "test server", "server"]
)
def test_get_skill_reference_accepts_normalized_and_partial_names(
    reference: str,
) -> None:
    result = CliRunner().invoke(
        main,
        args=["get", "skill", "--name", "shiny-for-python", "--reference", reference],
    )

    assert result.exit_code == 0
    assert "test_server" in result.output


def test_get_skill_reference_reports_ambiguous_names() -> None:
    result = CliRunner().invoke(
        main,
        args=["get", "skill", "--name", "shiny-for-python", "--reference", "modules"],
    )

    assert result.exit_code != 0
    assert "ambiguous" in result.output
    assert "modules-core" in result.output
    assert "modules-express" in result.output


def test_get_skill_reference_reports_unknown_names() -> None:
    result = CliRunner().invoke(
        main,
        args=["get", "skill", "--name", "shiny-for-python", "--reference", "zzzzzz"],
    )

    assert result.exit_code != 0
    assert "Unknown reference 'zzzzzz'" in result.output
    assert "Available references:" in result.output
    assert "reactivity" in result.output


def test_get_skill_reports_unknown_skill_names() -> None:
    result = CliRunner().invoke(main, args=["get", "skill", "--name", "unknown-skill"])

    assert result.exit_code != 0
    assert "Unknown skill 'unknown-skill'" in result.output
    assert "shiny-for-python" in result.output


def test_get_skill_requires_a_name() -> None:
    result = CliRunner().invoke(main, args=["get", "skill"])

    assert result.exit_code != 0
    assert "Missing option '--name'" in result.output


def test_get_skill_reads_the_named_skill(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "other-skill"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "# Other skill\nRead `references/example.md`.\n", encoding="utf-8"
    )
    (references_dir / "example.md").write_text(
        "# Example\nRead `references/example-extra.md`.\n", encoding="utf-8"
    )
    (references_dir / "example-extra.md").write_text("# Extra\n", encoding="utf-8")
    monkeypatch.setattr(_skills, name="SKILLS_DIR", value=tmp_path)

    index = CliRunner().invoke(main, args=["get", "skill", "--name", "other-skill"])
    reference = CliRunner().invoke(
        main, args=["get", "skill", "--name", "other-skill", "--reference", "example"]
    )

    assert index.exit_code == 0
    assert "# Other skill" in index.output
    assert "`shiny get skill --name other-skill --reference example`" in index.output
    assert reference.exit_code == 0
    assert "# Example" in reference.output
    assert (
        "`shiny get skill --name other-skill --reference example-extra`"
        in reference.output
    )


def test_get_skill_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_skills, name="SKILLS_DIR", value=tmp_path / "nonexistent")

    result = CliRunner().invoke(
        main, args=["get", "skill", "--name", "shiny-for-python"]
    )

    assert result.exit_code != 0
    assert "No skills are bundled" in result.output


def test_get_skill_reference_cannot_read_files_outside_the_skill(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "sample"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
    (references_dir / "example.md").write_text("# Example\n", encoding="utf-8")
    (tmp_path / "private.md").write_text("private contents", encoding="utf-8")
    monkeypatch.setattr(_skills, name="SKILLS_DIR", value=tmp_path)

    result = CliRunner().invoke(
        main, args=["get", "skill", "--name", "sample", "--reference", "../../private"]
    )

    assert result.exit_code != 0
    assert "Unknown reference" in result.output
    assert "private contents" not in result.output


def test_get_skill_reports_missing_references(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "sample"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
    monkeypatch.setattr(_skills, name="SKILLS_DIR", value=tmp_path)

    result = CliRunner().invoke(
        main, args=["get", "skill", "--name", "sample", "--reference", "example"]
    )

    assert result.exit_code != 0
    assert "No references are bundled with skill 'sample'" in result.output
