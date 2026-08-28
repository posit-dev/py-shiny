from __future__ import annotations

from pathlib import Path

import pytest

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.pytest import (
    AsyncTestServerSession,
    TestServerSession,
    test_server,
    test_server_async,
)
from shiny.testmode import export_test_values


def test_interactive_context_manager():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    with test_server(server) as s:
        assert isinstance(s, TestServerSession)
        s.set_inputs(n=10)
        assert s.get_output("doubled") == "Result: 20"
        assert s.outputs["doubled"] == "Result: 20"

        s.set_inputs(n=25)
        assert s.get_output("doubled") == "Result: 50"
        assert s.outputs["doubled"] == "Result: 50"


def test_interactive_callback_syntax():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    def test_logic(s: TestServerSession):
        s.set_inputs(n=5)
        assert s.outputs["doubled"] == "Result: 10"

        s.set_inputs(n=15)
        assert s.outputs["doubled"] == "Result: 30"

    test_server(server, test_logic)


@pytest.mark.asyncio
async def test_interactive_async_context_manager():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def squared():
            return f"{input.x() ** 2}"

    async with test_server_async(server) as s:
        assert isinstance(s, AsyncTestServerSession)
        await s.set_inputs(x=3)
        assert s.outputs["squared"] == "9"

        await s.set_inputs(x=7)
        assert s.outputs["squared"] == "49"


def test_interactive_exports():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return str(input.val())

        export_test_values(doubled=lambda: input.val() * 2)

    with test_server(server) as s:
        s.set_inputs(val=10)
        assert s.exports["doubled"] == 20
        assert s.get_export("doubled") == 20

        s.set_inputs(val=40)
        assert s.exports["doubled"] == 80
        assert s.get_export("doubled") == 80


def test_test_server_direct_server_function():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    res = test_server(server, inputs={"n": 25})
    assert res.success is True
    assert res.outputs["doubled"] == "Result: 50"
    assert res.elapsed_ms > 0


def test_test_server_direct_app_instance():
    app_ui = ui.page_fluid(
        ui.input_numeric("n", "N", value=10),
        ui.output_text("doubled"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    app = App(app_ui, server)

    res = test_server(app, inputs={"n": 25})
    assert res.success is True
    assert res.outputs["doubled"] == "Result: 50"
    assert res.elapsed_ms > 0


def test_test_server_express_code():
    code = """from shiny.express import input, render, ui
ui.input_slider("n", "N", 1, 100, 20)
@render.text
def doubled():
    return f"Result: {input.n() * 2}"
"""
    res = test_server(code=code, inputs={"n": 30})
    assert res.success is True
    assert res.outputs["doubled"] == "Result: 60"


def test_test_server_file_path(tmp_path: Path):
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

    res = test_server(app_file, inputs={"txt": "pytest-sim"})
    assert res.success is True
    assert res.outputs["out"] == "Echo: pytest-sim"


def test_test_server_reactive_errors():
    app_ui = ui.page_fluid(
        ui.output_text("err_out"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def err_out():
            raise ValueError("Custom calculation error")

    app = App(app_ui, server)
    res = test_server(app)
    assert res.success is False
    assert "err_out" in res.errors
    assert "Custom calculation error" in str(res.errors["err_out"])


def test_test_server_initialization_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        raise RuntimeError("Fatal server init crash")

    app = App(app_ui, server)
    res = test_server(app)

    assert res.success is False
    assert "Fatal server init crash" in str(res.error)


def test_test_server_reactive_effect_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        def _():
            raise RuntimeError("Fatal effect crash")

    app = App(app_ui, server)
    res = test_server(app)

    assert res.success is False
    assert "Fatal effect crash" in str(res.error)


def test_test_server_restores_app_test_mode_and_server():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "ok"

    app = App(app_ui, server, test_mode=False)
    original_server = app.server
    assert app._test_mode is False

    res = test_server(app)
    assert res.success is True
    assert app._test_mode is False
    assert app.server is original_server


def test_test_server_mapping_interface():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "simulated"

    app = App(app_ui, server)
    res = test_server(app)

    assert res["outputs"]["out"] == "simulated"
    assert "outputs" in res
    assert len(res) == 7
    assert res.get("outputs") == {"out": "simulated"}
    assert res.to_dict()["success"] is True
