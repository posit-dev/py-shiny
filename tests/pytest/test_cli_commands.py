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


def test_cli_simulate_express():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_slider("n", "N", 1, 100, 20)
@render.text
def doubled():
    return f"Result: {input.n() * 2}"
"""
    res = runner.invoke(main, ["simulate", "--code", code, "-i", "n=30"])
    assert res.exit_code == 0
    assert "Simulation completed successfully" in res.output
    assert "doubled: Result: 60" in res.output


def test_cli_simulate_json():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_slider("val", "Val", 1, 10, 2)
@render.text
def out():
    return f"Val={input.val()}"
"""
    res = runner.invoke(
        main,
        ["simulate", "--code", code, "--inputs", '{"val": 8}', "--json"],
    )
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["success"] is True
    assert data["outputs"]["out"] == "Val=8"
    assert "elapsed_ms" in data


def test_cli_simulate_runtime_error():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
@render.text
def err_out():
    raise ValueError("Intentional crash")
"""
    res = runner.invoke(main, ["simulate", "--code", code])
    assert res.exit_code == 1
    assert "Simulation failed" in res.output
    assert "Intentional crash" in res.output


def test_cli_inspect_text():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
from shiny import reactive
ui.input_slider("n", "N", 1, 10, 5)
@reactive.calc
def calc_val():
    return input.n() * 10
@render.text
def out_val():
    return f"Out: {calc_val()}"
"""
    res = runner.invoke(main, ["inspect", "--code", code])
    assert res.exit_code == 0
    assert "input.n" in res.output
    assert "calc_val" in res.output
    assert "out_val" in res.output


def test_cli_inspect_mermaid():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_text("txt", "Text")
@render.text
def out():
    return input.txt()
"""
    res = runner.invoke(main, ["inspect", "--code", code, "--mermaid"])
    assert res.exit_code == 0
    assert "graph TD" in res.output
    assert "txt" in res.output


def test_cli_inspect_json():
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_numeric("count", "Count", 10)
@render.text
def display():
    return f"Count: {input.count()}"
"""
    res = runner.invoke(main, ["inspect", "--code", code, "--json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["success"] is True
    assert len(data["nodes"]) >= 2
    assert len(data["edges"]) >= 1


def test_cli_docs_list():
    runner = CliRunner()
    res = runner.invoke(main, ["docs"])
    assert res.exit_code == 0
    assert "Shiny for Python Components" in res.output
    assert "ui.page_sidebar" in res.output


def test_cli_docs_category():
    runner = CliRunner()
    res = runner.invoke(main, ["docs", "-c", "inputs"])
    assert res.exit_code == 0
    assert "ui.input_slider" in res.output
    assert "ui.page_sidebar" not in res.output


def test_cli_docs_component():
    runner = CliRunner()
    res = runner.invoke(main, ["docs", "ui.page_sidebar"])
    assert res.exit_code == 0
    assert "ui.page_sidebar" in res.output
    assert "Signature:" in res.output
    assert "Example Snippet:" in res.output


def test_cli_docs_json():
    runner = CliRunner()
    res = runner.invoke(main, ["docs", "render.plot", "--json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["name"] == "render.plot"
    assert data["category"] == "renderers"
