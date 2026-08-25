from __future__ import annotations

import json
import time
from pathlib import Path

from click.testing import CliRunner

from shiny._main import main


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


def test_cli_simulate_timeout_stops_synchronous_blocking_code():
    runner = CliRunner()
    code = """import time
from shiny.express import render
@render.text
def blocked():
    time.sleep(3)
    return "finished"
"""

    started = time.monotonic()
    res = runner.invoke(main, ["simulate", "--code", code, "--timeout", "0.2"])
    elapsed = time.monotonic() - started

    assert res.exit_code == 1
    assert "timed out after 0.2s" in res.output
    assert elapsed < 2


def test_cli_simulate_core_app_can_import_sibling_module(tmp_path: Path):
    runner = CliRunner()
    (tmp_path / "helpers.py").write_text(
        "def message():\n    return 'loaded sibling'\n", encoding="utf-8"
    )
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny import App, render, ui
from helpers import message

app_ui = ui.page_fluid(ui.output_text("result"))

def server(input, output, session):
    @render.text
    def result():
        return message()

app = App(app_ui, server)
""",
        encoding="utf-8",
    )

    res = runner.invoke(main, ["simulate", str(app_file)])

    assert res.exit_code == 0
    assert "result: loaded sibling" in res.output
