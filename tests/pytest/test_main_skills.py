import json
import re
import sys
from pathlib import Path
from typing import cast

import pytest
from click.testing import CliRunner

from shiny._main import _skills as _main_skills
from shiny._main import main

SKILLS_DIR = Path(_main_skills.__file__).parent.parent / ".agents" / "skills"
SKILL_NAME = "shiny-for-python"


def test_skills_list_shows_names_and_descriptions() -> None:
    result = CliRunner().invoke(main, ["skills", "list"])

    assert result.exit_code == 0
    assert SKILL_NAME in result.output
    skill_line = next(line for line in result.output.splitlines() if SKILL_NAME in line)
    assert skill_line.startswith(f"{SKILL_NAME}  ")
    skill_md = (SKILLS_DIR / SKILL_NAME / "SKILL.md").read_text()
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


def test_skills_path_prints_skill_directory() -> None:
    result = CliRunner().invoke(main, ["skills", "path", SKILL_NAME])

    assert result.exit_code == 0
    assert result.output == f"{SKILLS_DIR / SKILL_NAME}\n"
    assert Path(result.output.strip()).is_absolute()


def test_skills_path_unknown_name_lists_available_skills() -> None:
    result = CliRunner().invoke(main, ["skills", "path", "does-not-exist"])

    assert result.exit_code != 0
    assert "does-not-exist" in result.output
    assert SKILL_NAME in result.output


def test_skills_path_with_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(_main_skills, "SKILLS_DIR", tmp_path / "nope")

    result = CliRunner().invoke(main, ["skills", "path", SKILL_NAME])

    assert result.exit_code != 0
    assert "No skills" in result.output


def test_skill_list_json() -> None:
    result = CliRunner().invoke(main, ["skill", "list", "--json"])
    assert result.exit_code == 0
    data = cast(list[dict[str, str]], json.loads(result.output))
    assert any(s["name"] == SKILL_NAME and s["package"] == "shiny" for s in data)


def _add_distribution(site: Path, package: str, *files: Path) -> Path:
    dist = site / f"{package.replace('-', '_')}-1.0.dist-info"
    dist.mkdir()
    (dist / "METADATA").write_text(f"Name: {package}\nVersion: 1.0\n", encoding="utf-8")
    record = "".join(f"{file.relative_to(site).as_posix()},,\n" for file in files)
    (dist / "RECORD").write_text(record, encoding="utf-8")
    return dist


def test_skill_list_discovers_ecosystem_packages(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pkg_dir = tmp_path / "widget_module" / ".agents" / "skills" / "custom-widget"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "SKILL.md").write_text(
        "---\nname: custom-widget\ndescription: Widget skill\n---\n# Custom\n",
        encoding="utf-8",
    )
    _add_distribution(tmp_path, "shiny-widgets-extension", pkg_dir / "SKILL.md")
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])

    result = CliRunner().invoke(main, ["skill", "list"])
    assert result.exit_code == 0
    assert "[shiny-widgets-extension] custom-widget" in result.output
    assert "Widget skill" in result.output

    legacy = CliRunner().invoke(main, ["skills", "list"])
    assert legacy.exit_code == 0
    assert "custom-widget" not in legacy.output


def test_skill_list_all_includes_general_packages(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pkg_dir = tmp_path / "otherpkg" / ".agents" / "skills" / "other-tool"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "SKILL.md").write_text(
        "---\nname: other-tool\ndescription: General tool skill\n---\n# Tool\n",
        encoding="utf-8",
    )
    _add_distribution(tmp_path, "otherpkg", pkg_dir / "SKILL.md")
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])

    default_res = CliRunner().invoke(main, ["skill", "list"])
    assert default_res.exit_code == 0
    assert "other-tool" not in default_res.output

    all_res = CliRunner().invoke(main, ["skill", "list", "--all"])
    assert all_res.exit_code == 0
    assert "[otherpkg] other-tool" in all_res.output


def test_skill_path_prefers_the_skill_shown_in_default_list(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for package in ("anotherlib", "shiny-extension"):
        path = tmp_path / package / ".agents" / "skills" / "shared-skill"
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(f"# {package}\n", encoding="utf-8")
        _add_distribution(tmp_path, package, path / "SKILL.md")
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])

    result = CliRunner().invoke(main, ["skill", "path", "shared-skill"])
    assert result.exit_code == 0
    assert Path(result.output.strip()) == (
        tmp_path / "shiny-extension" / ".agents" / "skills" / "shared-skill"
    )


def test_skill_list_discovers_entry_points(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "ep-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: ep-skill\ndescription: EP description\n---\n# EP\n",
        encoding="utf-8",
    )

    module = tmp_path / "sample_skill_provider.py"
    module.write_text(
        "from pathlib import Path\n"
        "skill = Path(__file__).parent / 'ep-skill'\n"
        "paths = {'ep-skill': skill, '../outside': skill}\n",
        encoding="utf-8",
    )
    dist = _add_distribution(tmp_path, "mockdist", module, skill_dir / "SKILL.md")
    (dist / "entry_points.txt").write_text(
        "[shiny.skills]\nsample = sample_skill_provider:paths\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])

    result = CliRunner().invoke(main, ["skill", "list"])
    assert result.exit_code == 0
    assert "[mockdist] ep-skill" in result.output
    assert "../outside" not in result.output


def test_skill_get_prints_skill_and_rewrites_references() -> None:
    result = CliRunner().invoke(main, ["skill", "get", SKILL_NAME])
    assert result.exit_code == 0
    assert "name: shiny-for-python" in result.output
    assert f"`shiny skill get {SKILL_NAME} --reference reactivity`" in result.output


def test_skill_get_with_name_option() -> None:
    result = CliRunner().invoke(main, ["skill", "get", "--name", SKILL_NAME])
    assert result.exit_code == 0
    assert "name: shiny-for-python" in result.output


def test_skill_get_reference() -> None:
    result = CliRunner().invoke(
        main, ["skill", "get", SKILL_NAME, "--reference", "reactivity"]
    )
    assert result.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result.output


def test_skill_get_missing_name_error() -> None:
    result = CliRunner().invoke(main, ["skill", "get"])
    assert result.exit_code != 0
    assert "Missing required skill name" in result.output


def test_skill_install_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["skill", "install", SKILL_NAME])
    assert result.exit_code == 0
    installed_path = tmp_path / ".agents" / "skills" / SKILL_NAME
    assert installed_path.exists()
    assert (installed_path / "SKILL.md").is_file()


def test_skill_install_claude(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["skill", "install", SKILL_NAME, "--claude"])
    assert result.exit_code == 0
    installed_path = tmp_path / ".claude" / "skills" / SKILL_NAME
    assert installed_path.exists()
    assert (installed_path / "SKILL.md").is_file()


def test_skill_install_copy(tmp_path: Path) -> None:
    target = tmp_path / "custom_target"
    result = CliRunner().invoke(
        main, ["skill", "install", SKILL_NAME, "--target", str(target), "--copy"]
    )
    assert result.exit_code == 0
    installed_path = target / SKILL_NAME
    assert installed_path.exists()
    assert not installed_path.is_symlink()
    assert (installed_path / "SKILL.md").is_file()


def test_skill_install_all(tmp_path: Path) -> None:
    target = tmp_path / "all_skills"
    result = CliRunner().invoke(
        main, ["skill", "install", "--all", "--target", str(target)]
    )
    assert result.exit_code == 0
    assert (target / SKILL_NAME).exists()


def test_skill_install_preserves_existing_directory(tmp_path: Path) -> None:
    target = tmp_path / "replace_target"
    first = CliRunner().invoke(
        main, ["skill", "install", SKILL_NAME, "--target", str(target), "--copy"]
    )
    assert first.exit_code == 0
    document = target / SKILL_NAME / "SKILL.md"
    document.write_text("# Project-specific edits\n", encoding="utf-8")
    second = CliRunner().invoke(
        main, ["skill", "install", SKILL_NAME, "--target", str(target), "--copy"]
    )
    assert second.exit_code != 0
    assert "already exists" in second.output
    assert document.read_text(encoding="utf-8") == "# Project-specific edits\n"


def test_skill_install_cleans_up_failed_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"

    def fail_copy(src: Path, dst: Path, **kwargs: object) -> None:
        dst.mkdir(exist_ok=True)
        (dst / "SKILL.md").touch()
        raise OSError("Disk full")

    monkeypatch.setattr(_main_skills.shutil, "copytree", fail_copy)
    result = CliRunner().invoke(
        main, ["skill", "install", SKILL_NAME, "--target", str(target), "--copy"]
    )

    assert result.exit_code != 0
    assert "Disk full" in result.output
    assert not (target / SKILL_NAME).exists()


def test_skill_install_missing_args() -> None:
    result = CliRunner().invoke(main, ["skill", "install"])
    assert result.exit_code != 0
    assert "Please specify a skill name" in result.output


def test_skill_get_reference_commands_all_resolve() -> None:
    result = CliRunner().invoke(main, ["skill", "get", SKILL_NAME])
    references = re.findall(
        rf"`shiny skill get {SKILL_NAME} --reference ([a-z0-9-]+)`",
        string=result.output,
    )
    assert references
    for reference in references:
        res = CliRunner().invoke(
            main, ["skill", "get", SKILL_NAME, "--reference", reference]
        )
        assert res.exit_code == 0, reference
        assert res.output.strip()


@pytest.mark.parametrize(
    "reference",
    argvalues=["reactivity", "REACTIVITY", "reactivity.md", "reactive", "reactivty"],
)
def test_skill_get_reference_accepts_close_names(reference: str) -> None:
    result = CliRunner().invoke(
        main, ["skill", "get", SKILL_NAME, "--reference", reference]
    )
    assert result.exit_code == 0
    assert "# Reactivity in Shiny for Python" in result.output
    assert "from shiny import reactive" in result.output
    assert f"`shiny skill get {SKILL_NAME} --reference extended-tasks`" in result.output
    assert "references/" not in result.output


@pytest.mark.parametrize(
    "reference", argvalues=["test_server", "test server", "server"]
)
def test_skill_get_reference_accepts_normalized_and_partial_names(
    reference: str,
) -> None:
    result = CliRunner().invoke(
        main, ["skill", "get", SKILL_NAME, "--reference", reference]
    )
    assert result.exit_code == 0
    assert "test_server" in result.output


def test_skill_get_reference_reports_ambiguous_names() -> None:
    result = CliRunner().invoke(
        main, ["skill", "get", SKILL_NAME, "--reference", "modules"]
    )
    assert result.exit_code != 0
    assert "ambiguous" in result.output
    assert "modules-core" in result.output
    assert "modules-express" in result.output


def test_skill_get_reference_reports_unknown_names() -> None:
    result = CliRunner().invoke(
        main, ["skill", "get", SKILL_NAME, "--reference", "zzzzzz"]
    )
    assert result.exit_code != 0
    assert "Unknown reference 'zzzzzz'" in result.output
    assert "Available references:" in result.output
    assert "reactivity" in result.output


def test_skill_get_reports_unknown_skill_names() -> None:
    result = CliRunner().invoke(main, ["skill", "get", "unknown-skill"])
    assert result.exit_code != 0
    assert "Unknown skill 'unknown-skill'" in result.output
    assert SKILL_NAME in result.output


def test_skill_get_reads_external_skill(
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
    monkeypatch.setattr(_main_skills, name="SKILLS_DIR", value=tmp_path)

    index = CliRunner().invoke(main, ["skill", "get", "other-skill"])
    reference = CliRunner().invoke(
        main, ["skill", "get", "other-skill", "--reference", "example"]
    )
    assert index.exit_code == 0
    assert "# Other skill" in index.output
    assert "`shiny skill get other-skill --reference example`" in index.output
    assert reference.exit_code == 0
    assert "# Example" in reference.output
    assert "`shiny skill get other-skill --reference example-extra`" in reference.output


def test_skill_get_reference_cannot_read_files_outside_the_skill(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "sample"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
    (references_dir / "example.md").write_text("# Example\n", encoding="utf-8")
    (tmp_path / "private.md").write_text("private contents", encoding="utf-8")
    monkeypatch.setattr(_main_skills, name="SKILLS_DIR", value=tmp_path)

    result = CliRunner().invoke(
        main, ["skill", "get", "sample", "--reference", "../../private"]
    )
    assert result.exit_code != 0
    assert "Unknown reference" in result.output
    assert "private contents" not in result.output


def test_skill_get_reference_ignores_symlink_outside_skill(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "sample"
    references = skill_dir / "references"
    references.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
    private = tmp_path / "private.md"
    private.write_text("private contents", encoding="utf-8")
    try:
        (references / "external.md").symlink_to(private)
    except OSError:
        pytest.skip("Symlinks are unavailable")
    monkeypatch.setattr(_main_skills, "SKILLS_DIR", tmp_path)

    result = CliRunner().invoke(
        main, ["skill", "get", "sample", "--reference", "external"]
    )
    assert result.exit_code != 0
    assert "private contents" not in result.output


def test_skill_get_reports_missing_references(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "sample"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
    monkeypatch.setattr(_main_skills, name="SKILLS_DIR", value=tmp_path)

    result = CliRunner().invoke(
        main, ["skill", "get", "sample", "--reference", "example"]
    )
    assert result.exit_code != 0
    assert "No references are bundled with skill 'sample'" in result.output
