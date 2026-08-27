from __future__ import annotations

import json
from pathlib import Path

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
    assert "All validation checks passed" in res.output
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
    code = """from shiny.express import input, render, ui
ui.input_slider("n", "N", 1, 10, 5)
@render.text
def txt():
    return f"Value: {input.n}"
"""
    res = runner.invoke(main, ["validate", "--code", code])
    assert res.exit_code == 0
    assert "UNCALLED_INPUT" in res.output


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
