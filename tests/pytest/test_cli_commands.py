from __future__ import annotations

import html as html_lib
import json
from pathlib import Path

from click.testing import CliRunner

from shiny._main import main


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


def test_cli_inspect_html_includes_escaped_source_code(tmp_path: Path):
    runner = CliRunner()
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
# <unsafe-demo-marker>
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    app_file = tmp_path / "app.py"
    html_file = tmp_path / "reactlog.html"
    app_file.write_text(code, encoding="utf-8")

    res = runner.invoke(main, ["inspect", str(app_file), "--html", str(html_file)])

    assert res.exit_code == 0
    html = html_file.read_text(encoding="utf-8")
    assert 'role="tab"' in html
    assert "App code" in html
    assert html_lib.escape("<unsafe-demo-marker>") in html
    assert "<unsafe-demo-marker>" not in html


def test_cli_inspect_directory_requires_app_py(tmp_path: Path):
    runner = CliRunner()
    (tmp_path / "helpers.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "dashboard.py").write_text(
        "from shiny.express import ui\nui.page_opts(title='Dashboard')\n",
        encoding="utf-8",
    )

    res = runner.invoke(main, ["inspect", str(tmp_path)])

    assert res.exit_code == 1
    assert "does not contain app.py" in res.output
