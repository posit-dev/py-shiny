from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from shiny._main import main


def test_cli_validate_valid_express():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.page_opts(title="Test")
ui.input_slider("n", "N", 1, 10, 5)
@render.text
def txt():
    return f"Value: {input.n()}"
"""
    res = runner.invoke(main, ["validate", "--code", code])
    assert res.exit_code == 0
    assert "No issues found by the enabled static checks" in res.output
    assert "Inputs (1): n" in res.output


def test_cli_validate_errors_json():
    runner = CliRunner()
    code = "from shiny import shinyApp, fluidPage\n"
    res = runner.invoke(main, ["validate", "--code", code, "--json"])
    assert res.exit_code == 1
    data = json.loads(res.output)
    assert data["valid"] is False
    assert any(e["code"] == "R_SHINY_IDIOM" for e in data["errors"])


def test_cli_validate_warnings():
    runner = CliRunner()
    code = """from shiny.express import ui
ui.input_slider("n", "N", 1, 10, 5)
ui.input_slider("n", "Second N", 1, 10, 5)
"""
    res = runner.invoke(main, ["validate", "--code", code])
    assert res.exit_code == 0
    assert "DUPLICATE_ID" in res.output
    assert "No errors found (1 warning)." in res.output
    assert "All validation checks passed" not in res.output
    assert runner.invoke(main, ["validate", "--code", code, "--strict"]).exit_code == 1


def test_cli_validate_warning_only_json() -> None:
    runner = CliRunner()
    code = """from shiny.express import ui
ui.input_slider("n", "N", 1, 10, 5)
ui.input_slider("n", "Second N", 1, 10, 5)
"""
    args = ["validate", "--code", code, "--json"]
    res = runner.invoke(main, args)
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["valid"] is True
    assert runner.invoke(main, [*args, "--strict"]).exit_code == 1
    assert {warning["code"] for warning in data["warnings"]} == {"DUPLICATE_ID"}
    assert (
        "Code structure matches Python Shiny best practices." not in data["suggestions"]
    )


def test_cli_validate_file(tmp_path: Path):
    runner = CliRunner()
    app_file = tmp_path / "app.py"
    app_file.write_text(
        "from shiny.express import ui\nui.page_opts(title='Hi')\n",
        encoding="utf-8",
    )
    res = runner.invoke(main, ["validate", str(app_file)])
    assert res.exit_code == 0
    assert "Validating" in res.output


def test_cli_validate_missing_file():
    runner = CliRunner()
    res = runner.invoke(main, ["validate", "nonexistent_file_123.py"])
    assert res.exit_code == 1
    assert "File not found" in res.output


def test_cli_validate_directory_requires_app_py(tmp_path: Path):
    runner = CliRunner()
    (tmp_path / "helpers.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "dashboard.py").write_text(
        "from shiny.express import ui\nui.page_opts(title='Dashboard')\n",
        encoding="utf-8",
    )

    res = runner.invoke(main, ["validate", str(tmp_path)])

    assert res.exit_code == 1
    assert "does not contain app.py" in res.output


def test_cli_validate_validator_option(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys

    (tmp_path / "cli_rules_mod.py").write_text(
        "import ast\n"
        "from shiny.validate import ValidationRule\n"
        "class NoPrint(ValidationRule):\n"
        "    def visit_Call(self, node):\n"
        "        if isinstance(node.func, ast.Name) and node.func.id == 'print':\n"
        "            self.result.add_error(node.lineno, 'No print', 'CLI_PRINT')\n"
        "        self.generic_visit(node)\n"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", list(sys.path))
    runner = CliRunner()
    args = ["validate", "--code", "print('hi')", "--json"]
    assert runner.invoke(main, args).exit_code == 0

    res = runner.invoke(main, [*args, "--validator", "cli_rules_mod:NoPrint"])
    assert res.exit_code == 1
    assert [e["code"] for e in json.loads(res.output)["errors"]] == ["CLI_PRINT"]


def test_cli_validate_bad_validator_spec() -> None:
    res = CliRunner().invoke(
        main, ["validate", "--code", "pass", "--validator", "no_such_mod_xyz:Rule"]
    )
    assert res.exit_code == 2
    assert "--validator" in res.output
    assert "ModuleNotFoundError" in res.output
