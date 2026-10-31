import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import main
from shiny._main._run import _validate_app_file
from shiny.validate import validate_shiny_file


@pytest.mark.parametrize("target", ["app.py", "."])
@pytest.mark.parametrize("json_output", [False, True])
def test_cli_checks_local_imports_without_executing_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str, json_output: bool
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "app.py").write_text("from allocation import server\n")
    imported = tmp_path / "allocation.py"
    imported.write_text("raise RuntimeError('must not execute')\ninput.n = 1\n")
    args = ["validate", target]
    if json_output:
        args.append("--json")
    response = CliRunner().invoke(main, args=args)
    assert response.exit_code == 1
    if json_output:
        errors = json.loads(response.output)["errors"]
        assert [(issue["file"], issue["line"], issue["code"]) for issue in errors] == [
            (str(imported), 2, "INPUT_ASSIGNMENT")
        ]
    else:
        assert f"{imported}:2" in response.output


def test_imported_package_relative_imports_and_cycles(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("from modules import allocation\n")
    package = tmp_path / "modules"
    package.mkdir()
    (package / "__init__.py").write_text("from . import allocation\n")
    (package / "allocation.py").write_text("from .nested import helper\ninput.a = 1\n")
    nested = package / "nested"
    nested.mkdir()
    (nested / "__init__.py").write_text("")
    (nested / "helper.py").write_text("from .. import allocation\ninput.b = 2\n")
    result = validate_shiny_file(app)
    assert sorted(
        (Path(issue.get("file", "")).name, issue["line"]) for issue in result.errors
    ) == [
        ("allocation.py", 2),
        ("helper.py", 2),
    ]


def test_only_imported_local_files_are_checked(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import unavailable_external_package\nfrom good import value\n")
    (tmp_path / "good.py").write_text("value = 1\n")
    (tmp_path / "unrelated.py").write_text("input.n = 1\n")
    assert validate_shiny_file(app).clean


def test_separate_module_ids_do_not_collide(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import first\nimport second\n")
    module_code = (
        "from shiny import module, ui\n@module.ui\ndef panel():\n"
        "    return ui.input_text('name', 'Name')\n"
    )
    (tmp_path / "first.py").write_text(module_code)
    (tmp_path / "second.py").write_text(module_code)
    assert validate_shiny_file(app).clean


def test_output_pairing_spans_imported_files(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text(
        "from shiny import App, ui\nfrom server import server\n"
        "app_ui = ui.page_fluid(ui.output_text('shown'), ui.output_text('orphan'))\n"
        "app = App(app_ui, server)\n"
    )
    server = tmp_path / "server.py"
    server.write_text(
        "from shiny import render\n"
        "def server(input, output, session):\n"
        "    @render.text\n    def shown():\n        return 'x'\n"
        "    @render.text\n"
        "    def debug_only():  # shiny: ignore RENDERER_WITHOUT_OUTPUT\n"
        "        return 'y'\n"
    )
    result = validate_shiny_file(app)
    assert [
        (Path(issue.get("file", "")).name, issue["line"], issue["code"])
        for issue in result.warnings
    ] == [("app.py", 3, "OUTPUT_WITHOUT_RENDERER")]


def test_imported_syntax_errors_are_reported(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import broken\n")
    broken = tmp_path / "broken.py"
    broken.write_text("def invalid(\n")
    result = validate_shiny_file(app)
    assert [(issue.get("file"), issue["code"]) for issue in result.errors] == [
        (str(broken), "SYNTAX_ERROR")
    ]


def test_suppressions_are_local_to_each_imported_file(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import other  # shiny: ignore\ninput.a = 1  # shiny: ignore\n")
    other = tmp_path / "other.py"
    other.write_text("input.b = 2\ninput.c = 3  # shiny: ignore INPUT_ASSIGNMENT\n")
    result = validate_shiny_file(app)
    assert [(issue.get("file"), issue["line"]) for issue in result.errors] == [
        (str(other), 1)
    ]


def test_absolute_import_does_not_load_app_directory_init(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import good\n")
    (tmp_path / "good.py").write_text("value = 1\n")
    (tmp_path / "__init__.py").write_text("input.n = 1\n")
    assert validate_shiny_file(app).clean


def test_symlink_cannot_pull_in_sources_outside_app(tmp_path: Path) -> None:
    directory = tmp_path / "app"
    directory.mkdir()
    app = directory / "app.py"
    app.write_text("import outside\n")
    outside = tmp_path / "outside.py"
    outside.write_text("input.n = 1\n")
    (directory / "outside.py").symlink_to(outside)
    assert validate_shiny_file(app).clean


def test_invalid_encoding_in_import_is_a_diagnostic(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import other\n")
    (tmp_path / "other.py").write_bytes(b"\xff\n")
    result = validate_shiny_file(app)
    assert [issue["code"] for issue in result.errors] == ["FILE_READ_ERROR"]


def test_imported_warning_respects_strict_mode(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    app.write_text("import other\n")
    (tmp_path / "other.py").write_text(
        "from shiny import reactive\nstate = reactive.value({})\n"
        "def update():\n    current = state()\n    current['x'] = 1\n    state.set(current)\n"
    )
    runner = CliRunner()
    assert runner.invoke(main, args=["validate", str(app)]).exit_code == 0
    assert runner.invoke(main, args=["validate", str(app), "--strict"]).exit_code == 1


def test_startup_diagnostics_name_the_imported_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    app = tmp_path / "app.py"
    app.write_text("import other\n")
    other = tmp_path / "other.py"
    other.write_text("input.n = 1\n")
    _validate_app_file(app)
    assert f"{other}:1" in capsys.readouterr().err
