from __future__ import annotations

import time
from pathlib import Path

import pytest

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.pytest import SimulationResult, simulate, simulate_async
from shiny.testmode import export_test_values


def test_simulate_direct_app_instance():
    app_ui = ui.page_fluid(
        ui.input_numeric("n", "N", value=10),
        ui.output_text("doubled"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    app = App(app_ui, server)

    res = simulate(app, inputs={"n": 25})
    assert isinstance(res, SimulationResult)
    assert res.success is True
    assert res.outputs["doubled"] == "Result: 50"
    assert res.elapsed_ms > 0


def test_simulate_express_code():
    code = """from shiny.express import input, render, ui
ui.input_slider("n", "N", 1, 100, 20)
@render.text
def doubled():
    return f"Result: {input.n() * 2}"
"""
    res = simulate(code=code, inputs={"n": 30})
    assert res.success is True
    assert res.outputs["doubled"] == "Result: 60"


def test_simulate_file_path(tmp_path: Path):
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny import App, Inputs, Outputs, Session, render, ui
app_ui = ui.page_fluid(ui.input_text("txt", "Text", value="initial"), ui.output_text("out"))
def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def out():
        return f"Echo: {input.txt()}"
app = App(app_ui, server)
""",
        encoding="utf-8",
    )

    res = simulate(app_file, inputs={"txt": "pytest-sim"})
    assert res.success is True
    assert res.outputs["out"] == "Echo: pytest-sim"


@pytest.mark.asyncio
async def test_simulate_async():
    app_ui = ui.page_fluid(
        ui.input_numeric("x", "X", value=3),
        ui.output_text("squared"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def squared():
            return f"{input.x() ** 2}"

    app = App(app_ui, server)
    res = await simulate_async(app, inputs={"x": 7})
    assert res.success is True
    assert res.outputs["squared"] == "49"


def test_simulate_test_exports():
    app_ui = ui.page_fluid(
        ui.input_numeric("val", "Val", value=10),
        ui.output_text("out"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return str(input.val())

        export_test_values(doubled=lambda: input.val() * 2)

    app = App(app_ui, server)
    res = simulate(app, inputs={"val": 40})
    assert res.success is True
    assert res.exports["doubled"] == 80


def test_simulate_reactive_errors():
    app_ui = ui.page_fluid(
        ui.output_text("err_out"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def err_out():
            raise ValueError("Custom calculation error")

    app = App(app_ui, server)
    res = simulate(app)
    assert res.success is False
    assert "err_out" in res.errors
    assert "Custom calculation error" in str(res.errors["err_out"])


def test_server_initialization_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        raise RuntimeError("Fatal server init crash")

    app = App(app_ui, server)
    res = simulate(app)

    assert res.success is False
    assert "Fatal server init crash" in str(res.error)


def test_reactive_effect_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        def _():
            raise RuntimeError("Fatal effect crash")

    app = App(app_ui, server)
    res = simulate(app)

    assert res.success is False
    assert "Fatal effect crash" in str(res.error)


def test_simulate_restores_app_test_mode():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "ok"

    app = App(app_ui, server, test_mode=False)
    assert app._test_mode is False

    res = simulate(app)
    assert res.success is True
    assert app._test_mode is False


def test_simulate_isolated_sibling_modules(tmp_path: Path):
    app_a_dir = tmp_path / "app_a"
    app_a_dir.mkdir()
    (app_a_dir / "helpers.py").write_text(
        "def message(): return 'Module A'", encoding="utf-8"
    )
    (app_a_dir / "app.py").write_text(
        """from shiny import App, render, ui
from helpers import message
app_ui = ui.page_fluid(ui.output_text("out"))
def server(input, output, session):
    @render.text
    def out(): return message()
app = App(app_ui, server)
""",
        encoding="utf-8",
    )

    app_b_dir = tmp_path / "app_b"
    app_b_dir.mkdir()
    (app_b_dir / "helpers.py").write_text(
        "def message(): return 'Module B'", encoding="utf-8"
    )
    (app_b_dir / "app.py").write_text(
        """from shiny import App, render, ui
from helpers import message
app_ui = ui.page_fluid(ui.output_text("out"))
def server(input, output, session):
    @render.text
    def out(): return message()
app = App(app_ui, server)
""",
        encoding="utf-8",
    )

    res_a = simulate(app_a_dir / "app.py")
    res_b = simulate(app_b_dir / "app.py")

    assert res_a.success is True
    assert res_a.outputs["out"] == "Module A"
    assert res_b.success is True
    assert res_b.outputs["out"] == "Module B"


def test_simulate_timeout_code_subprocess():
    code = """import time
from shiny.express import render
@render.text
def blocked():
    time.sleep(3)
    return "done"
"""
    started = time.monotonic()
    res = simulate(code=code, timeout_secs=0.2)
    elapsed = time.monotonic() - started

    assert res.success is False
    assert "timed out after 0.2s" in str(res.error)
    assert elapsed < 2


def test_simulate_mapping_interface():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "simulated"

    app = App(app_ui, server)
    res = simulate(app)

    assert res["outputs"]["out"] == "simulated"
    assert "outputs" in res
    assert len(res) == 7
    assert res.get("outputs") == {"out": "simulated"}
    assert res.to_dict()["success"] is True
