from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable

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

    with test_server(server) as ts:
        ts.set_inputs({"n": 25})
        assert ts.success is True
        assert ts.outputs["doubled"] == "Result: 50"
        assert ts.elapsed_ms > 0


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

    with test_server(app) as ts:
        ts.set_inputs({"n": 25})
        assert ts.success is True
        assert ts.outputs["doubled"] == "Result: 50"
        assert ts.elapsed_ms > 0


def test_test_server_express_code():
    code = """from shiny.express import input, render, ui
ui.input_slider("n", "N", 1, 100, 20)
@render.text
def doubled():
    return f"Result: {input.n() * 2}"
"""
    with test_server(code=code) as ts:
        ts.set_inputs({"n": 30})
        assert ts.success is True
        assert ts.outputs["doubled"] == "Result: 60"


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

    with test_server(app_file) as ts:
        ts.set_inputs({"txt": "pytest-sim"})
        assert ts.success is True
        assert ts.outputs["out"] == "Echo: pytest-sim"


def test_test_server_reactive_errors():
    app_ui = ui.page_fluid(
        ui.output_text("err_out"),
    )

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def err_out():
            raise ValueError("Custom calculation error")

    app = App(app_ui, server)
    with test_server(app) as ts:
        assert ts.success is False
        assert "err_out" in ts.errors
        assert "Custom calculation error" in str(ts.errors["err_out"])


def test_test_server_initialization_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        raise RuntimeError("Fatal server init crash")

    app = App(app_ui, server)
    with test_server(app) as ts:
        assert ts.success is False
        assert "Fatal server init crash" in str(ts.error)


def test_test_server_reactive_effect_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        def _():
            raise RuntimeError("Fatal effect crash")

    app = App(app_ui, server)
    with test_server(app) as ts:
        assert ts.success is False
        assert "Fatal effect crash" in str(ts.error)


def test_test_server_restores_app_test_mode_and_server():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "ok"

    app = App(app_ui, server, test_mode=False)
    original_server = app.server
    assert app._test_mode is False

    with test_server(app) as ts:
        assert ts.success is True

    assert app._test_mode is False
    assert app.server is original_server


def test_test_server_result_mapping_interface():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "simulated"

    app = App(app_ui, server)
    with test_server(app) as ts:
        res = ts.to_result()

    # The captured result outlives the `with` block.
    assert res["outputs"]["out"] == "simulated"
    assert "outputs" in res
    assert len(res) == 7
    assert res.get("outputs") == {"out": "simulated"}
    assert res.to_dict()["success"] is True


def test_test_server_startup_failure_cleans_up_environment(tmp_path: Path):
    orig_path = list(sys.path)
    orig_testmode = os.environ.get("SHINY_TESTMODE")

    bad_file = tmp_path / "bad_app.py"
    bad_file.write_text("import non_existent_package_xyz_123\n", encoding="utf-8")

    with pytest.raises(ModuleNotFoundError):
        with test_server(bad_file):
            pass

    assert sys.path == orig_path
    assert os.environ.get("SHINY_TESTMODE") == orig_testmode

    with pytest.raises(FileNotFoundError):
        with test_server(tmp_path / "does_not_exist.py"):
            pass

    assert sys.path == orig_path
    assert os.environ.get("SHINY_TESTMODE") == orig_testmode


def test_test_server_sibling_module_isolation(tmp_path: Path):
    dir_a = tmp_path / "app_a"
    dir_a.mkdir()
    (dir_a / "helpers.py").write_text("VALUE = 'from_A'\n", encoding="utf-8")
    (dir_a / "app.py").write_text(
        """from shiny import App, Inputs, Outputs, Session, render, ui
import helpers
app_ui = ui.page_fluid(ui.output_text("txt"))
def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def txt():
        return helpers.VALUE
app = App(app_ui, server)
""",
        encoding="utf-8",
    )

    dir_b = tmp_path / "app_b"
    dir_b.mkdir()
    (dir_b / "helpers.py").write_text("VALUE = 'from_B'\n", encoding="utf-8")
    (dir_b / "app.py").write_text(
        """from shiny import App, Inputs, Outputs, Session, render, ui
import helpers
app_ui = ui.page_fluid(ui.output_text("txt"))
def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def txt():
        return helpers.VALUE
app = App(app_ui, server)
""",
        encoding="utf-8",
    )

    with test_server(dir_a / "app.py") as ts:
        assert ts.outputs["txt"] == "from_A"

    with test_server(dir_b / "app.py") as ts:
        assert ts.outputs["txt"] == "from_B"


def test_test_server_set_inputs_timeout():
    import time

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        def _():
            val = input.hang()
            if val is not None and val > 0:
                time.sleep(1.0)

    with test_server(server, timeout_secs=0.2) as s:
        with pytest.raises(TimeoutError):
            s.set_inputs(hang=1)


@pytest.mark.asyncio
async def test_test_server_inside_running_loop_points_at_async_variant():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def txt():
            return "hi"

    with pytest.raises(RuntimeError, match="test_server_async"):
        with test_server(server):
            pass


USES_OF_A_RUNNING_SESSION: list[Callable[[TestServerSession], object]] = [
    lambda ts: ts.set_inputs(x=1),
    lambda ts: ts.flush(),
    lambda ts: ts.outputs,
    lambda ts: ts.exports,
    lambda ts: ts.errors,
    lambda ts: ts.success,
    lambda ts: ts.error,
    lambda ts: ts.traceback,
    lambda ts: ts.elapsed_ms,
    lambda ts: ts.get_output("out"),
    lambda ts: ts.get_export("out"),
    lambda ts: ts.to_result(),
    lambda ts: ts.to_dict(),
]
"""Every member that needs a started session, to check each one refuses to autostart."""


@pytest.mark.parametrize("use_session", USES_OF_A_RUNNING_SESSION)
def test_test_server_requires_a_context_manager(
    use_session: Callable[[TestServerSession], object],
):
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "ok"

    ts = test_server(server)
    with pytest.raises(RuntimeError, match="with test_server"):
        use_session(ts)


def test_test_server_set_inputs_chains_within_a_with_block():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"{input.n() * 2}"

    with test_server(server) as ts:
        assert ts.set_inputs(n=10).set_inputs(n=21) is ts
        assert ts.get_output("doubled") == "42"


def test_test_server_cleans_up_when_the_body_raises():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "ok"

    app = App(app_ui, server, test_mode=False)
    original_server = app.server

    with pytest.raises(AssertionError, match="boom"):
        with test_server(app) as ts:
            assert ts.get_output("out") == "ok"
            raise AssertionError("boom")

    assert "SHINY_TESTMODE" not in os.environ
    assert app._test_mode is False
    assert app.server is original_server


@pytest.mark.asyncio
async def test_async_set_inputs_returns_self():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def squared():
            return f"{input.x() ** 2}"

    async with test_server_async(server) as s:
        assert await s.set_inputs(x=6) is s
        assert s.outputs["squared"] == "36"


def test_set_inputs_merges_across_calls_and_never_stalls():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def both():
            return f"a={input.a()} b={input.b()}"

    with test_server(server) as ts:
        ts.set_inputs(a=1, b=2)
        assert ts.get_output("both") == "a=1 b=2"

        # A later call updates only the ids it names; `b` keeps its value.
        ts.set_inputs(a=9)
        assert ts.get_output("both") == "a=9 b=2"

        # Re-sending an unchanged value invalidates nothing, and setting an id no
        # output reads invalidates nothing either. Both must still flush, or
        # `set_inputs` would block until `timeout_secs`.
        ts.set_inputs(a=9)
        ts.set_inputs(unrelated=100)
        assert ts.get_output("both") == "a=9 b=2"

        # Falsy values are values, not "unset".
        ts.set_inputs(a=0, b=0)
        assert ts.get_output("both") == "a=0 b=0"

        # The degenerate calls must flush too, for the same reason.
        ts.set_inputs()
        ts.flush()
        ts.flush()
        assert ts.get_output("both") == "a=0 b=0"


def test_set_inputs_clears_errors_once_a_later_flush_succeeds():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def checked():
            if input.val() < 0:
                raise ValueError("must be non-negative")
            return f"ok {input.val()}"

        export_test_values(tripled=lambda: input.val() * 3)

    with test_server(server) as ts:
        ts.set_inputs(val=5)
        assert ts.success is True
        assert ts.get_export("tripled") == 15

        ts.set_inputs(val=-1)
        assert ts.success is False
        assert "must be non-negative" in str(ts.errors["checked"])

        # The snapshot is rebuilt per flush, so a recovered output stops reporting
        # the stale error.
        ts.set_inputs(val=7)
        assert ts.success is True
        assert ts.errors == {}
        assert ts.get_output("checked") == "ok 7"
        assert ts.get_export("tripled") == 21


@pytest.mark.asyncio
async def test_async_set_inputs_repeats_within_one_session():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def squared():
            return f"{input.x() ** 2}"

    async with test_server_async(server) as ts:
        for i in range(5):
            await ts.set_inputs(x=i)
            assert ts.get_output("squared") == str(i**2)
