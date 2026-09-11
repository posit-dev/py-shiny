from __future__ import annotations

import dataclasses
import importlib.util
import os
import sys
from pathlib import Path
from typing import Callable

import pytest

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.pytest import (
    AsyncTestServerSession,
    TestServerSession,
    TestServerValue,
    TestServerValues,
    test_server,
    test_server_async,
)
from shiny.testmode import export_test_values
from shiny.testserver._test_server import VALUE_FIELDS


def test_interactive_context_manager():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    with test_server(server) as s:
        assert isinstance(s, TestServerSession)
        s.set_inputs(n=10)
        assert s.get_output("doubled") == "Result: 20"
        assert s.get_output("doubled") == "Result: 20"

        s.set_inputs(n=25)
        assert s.get_output("doubled") == "Result: 50"
        assert s.get_output("doubled") == "Result: 50"


@pytest.mark.asyncio
async def test_interactive_async_context_manager():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def squared():
            return f"{input.x() ** 2}"

    async with test_server_async(server) as s:
        assert isinstance(s, AsyncTestServerSession)
        await s.set_inputs(x=3)
        assert s.get_output("squared") == "9"

        await s.set_inputs(x=7)
        assert s.get_output("squared") == "49"


def test_interactive_exports():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return str(input.val())

        export_test_values(doubled=lambda: input.val() * 2)

    with test_server(server) as s:
        s.set_inputs(val=10)
        assert s.get_export("doubled") == 20
        assert s.get_export("doubled") == 20

        s.set_inputs(val=40)
        assert s.get_export("doubled") == 80
        assert s.get_export("doubled") == 80


def test_test_server_direct_server_function():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def doubled():
            return f"Result: {input.n() * 2}"

    with test_server(server) as ts:
        ts.set_inputs({"n": 25})
        assert ts.success is True
        assert ts.get_output("doubled") == "Result: 50"


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
        assert ts.get_output("doubled") == "Result: 50"


EXPRESS_APP_SRC = """from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 100, 20)


@render.text
def greeting():
    return "express loaded"


@render.text
def doubled():
    return f"Result: {input.n() * 2}"
"""


def test_test_server_express_app_file(tmp_path: Path):
    """Express apps are module-level code, so they can only be loaded from a file."""
    app_file = tmp_path / "express_app.py"
    app_file.write_text(EXPRESS_APP_SRC, encoding="utf-8")

    with test_server(app_file) as ts:
        assert ts.success is True
        # An output with no input dependency renders straight away.
        assert ts.get_output("greeting") == "express loaded"
        # There is no browser to report the slider's value, so `input.n()` raises
        # a silent exception and `doubled` renders nothing -- without failing.
        assert ts.get_output("doubled").status == "silent"
        # Silent is not an error: nothing rendered, nothing failed.
        assert ts.get_output("doubled").error is None

        ts.set_inputs(n=30)
        assert ts.success is True
        assert ts.get_output("doubled") == "Result: 60"


def test_test_server_express_app_via_default_app_py(tmp_path: Path):
    """An Express `app.py` is found by the same caller-relative default as Core."""
    (tmp_path / "app.py").write_text(EXPRESS_APP_SRC, encoding="utf-8")
    call = _call_from_module(tmp_path, "test_server()", output="greeting")
    assert call == "express loaded"


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
        assert ts.get_output("out") == "Echo: pytest-sim"


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
        assert "Custom calculation error" in str(ts.get_output("err_out").error)


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


def test_test_server_values_snapshot_and_dict_conversion():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def out():
            return "simulated"

    app = App(app_ui, server)
    with test_server(app) as ts:
        values = ts.to_values()
        as_dict = dict(ts)

    # Both hold copies, so they outlive the `with` block.
    assert isinstance(values, TestServerValues)
    assert values.outputs["out"] == "simulated"
    assert values.success is True
    assert values.traceback == ""

    # `dict(session)` unpacks the snapshot's fields but keeps each rich value,
    # while `dataclasses.asdict` recurses all the way down to plain data.
    assert sorted(as_dict) == sorted(VALUE_FIELDS)
    assert as_dict["outputs"]["out"] is values.outputs["out"]
    assert dataclasses.asdict(values)["outputs"]["out"] == {
        "name": "out",
        "kind": "output",
        "status": "ok",
        "value": "simulated",
        "error": None,
        "traceback": "",
    }


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
        assert ts.get_output("txt") == "from_A"

    with test_server(dir_b / "app.py") as ts:
        assert ts.get_output("txt") == "from_B"


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
    lambda ts: ts.success,
    lambda ts: ts.error,
    lambda ts: ts.get_output("out"),
    lambda ts: ts.get_export("out"),
    lambda ts: ts.get_input("a"),
    lambda ts: ts.to_values(),
    lambda ts: dict(ts),
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
        assert s.get_output("squared") == "36"


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
        assert "must be non-negative" in str(ts.get_output("checked").error)

        # The snapshot is rebuilt per flush, so a recovered output stops reporting
        # the stale error.
        ts.set_inputs(val=7)
        assert ts.success is True
        assert ts.get_output("checked").error is None
        assert ts.get_output("checked").traceback == ""
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


APP_SRC = """from shiny import App, Inputs, Outputs, Session, render, ui
app_ui = ui.page_fluid(ui.output_text("out"))
def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def out():
        return "loaded {name}"
app = App(app_ui, server)
"""


def _call_from_module(tmp_path: Path, call_src: str, output: str = "out") -> str:
    """
    Run `with <call_src> as ts: ...` from a module living in `tmp_path`.

    `test_server()` resolves relative paths against its *caller's* directory, so
    the call has to happen from a file in `tmp_path` for the resolution to be
    exercised at all. Importing a throwaway module is the only way to move the
    calling frame.
    """
    mod_path = tmp_path / "caller_module.py"
    mod_path.write_text(
        "from shiny.pytest import test_server\n"
        "\n"
        "def run():\n"
        f"    with {call_src} as ts:\n"
        f"        return ts.get_output({output!r})\n",
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location("caller_module", mod_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["caller_module"] = mod
    try:
        spec.loader.exec_module(mod)
        return mod.run()
    finally:
        sys.modules.pop("caller_module", None)


def test_test_server_defaults_to_app_py_beside_the_caller(tmp_path: Path):
    (tmp_path / "app.py").write_text(APP_SRC.format(name="app.py"), encoding="utf-8")
    assert _call_from_module(tmp_path, "test_server()") == "loaded app.py"


def test_test_server_resolves_a_relative_str_against_the_caller(tmp_path: Path):
    (tmp_path / "myapp.py").write_text(
        APP_SRC.format(name="myapp.py"), encoding="utf-8"
    )
    # Not the process working directory: pytest runs from the repo root, where
    # `myapp.py` does not exist.
    assert not (Path.cwd() / "myapp.py").exists()
    assert _call_from_module(tmp_path, "test_server('myapp.py')") == "loaded myapp.py"


def test_test_server_uses_an_existing_path_as_is(tmp_path: Path):
    nested = tmp_path / "elsewhere"
    nested.mkdir()
    (nested / "app.py").write_text(APP_SRC.format(name="absolute"), encoding="utf-8")

    # An absolute `Path` that is already a file is never made caller-relative,
    # even though the caller's directory holds a different `app.py`.
    (tmp_path / "app.py").write_text(APP_SRC.format(name="app.py"), encoding="utf-8")
    call = f"test_server(__import__('pathlib').Path({str(nested / 'app.py')!r}))"
    assert _call_from_module(tmp_path, call) == "loaded absolute"


def test_test_server_missing_default_app_reports_the_resolved_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="app.py"):
        _call_from_module(tmp_path, "test_server()")


def test_test_server_rejects_an_unusable_target():
    with pytest.raises(TypeError, match="must be a server function"):
        with test_server(123):  # pyright: ignore[reportArgumentType]
            pass


def test_test_server_value_compares_against_the_raw_value():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def txt():
            return "hi"

    with test_server(server) as ts:
        got = ts.get_output("txt")
        assert isinstance(got, TestServerValue)
        assert got == "hi"
        assert got != "bye"
        assert got.value == "hi"

        # Comparing two rich values compares every field, not just the value.
        assert got == TestServerValue("txt", "output", "ok", "hi")
        assert got != TestServerValue("other", "output", "ok", "hi")

        # Equality is against arbitrary values, so instances are unhashable.
        with pytest.raises(TypeError):
            hash(got)


def test_test_server_value_statuses():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def fine():
            return "ok"

        @render.text
        def needs_input():
            return f"{input.n()}"

        @render.text
        def boom():
            raise ValueError("kaboom")

    with test_server(server) as ts:
        assert ts.get_output("fine").status == "ok"
        # Never rendered: `input.n()` is unset, so it raised a silent exception.
        assert ts.get_output("needs_input").status == "silent"
        assert ts.get_output("boom").status == "error"
        assert ts.get_output("no_such_output").status == "missing"

        # A silent output is not a failure; an errored one is.
        assert ts.success is False
        assert "boom" in str(ts.error)

        ts.set_inputs(n=5)
        assert ts.get_output("needs_input") == "5"
        assert ts.get_output("needs_input").status == "ok"


def test_test_server_value_records_a_per_item_traceback():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def boom():
            raise ValueError("kaboom")

    with test_server(server) as ts:
        failed = ts.get_output("boom")
        assert failed.error == "kaboom"
        # The traceback names the raising line, which the message alone does not.
        assert "ValueError: kaboom" in failed.traceback
        assert "raise ValueError" in failed.traceback

        # It is cleared once the output succeeds again.
        assert ts.get_output("boom").traceback != ""


def test_test_server_exposes_inputs():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def echo():
            return f"{input.a()}"

    with test_server(server) as ts:
        assert ts.get_input("a").status == "missing"

        ts.set_inputs(a=1, b="two")
        assert ts.get_input("a") == 1
        assert ts.get_input("b") == "two"
        assert ts.get_input("b").kind == "input"
        assert sorted(ts.to_values().inputs) == ["a", "b"]


def test_test_server_plot_is_silent_until_the_client_size_is_known():
    plt = pytest.importorskip("matplotlib.pyplot")

    def server(input: Inputs, output: Outputs, session: Session):
        @render.plot
        def a_plot():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])
            return fig

    with test_server(server) as ts:
        # No browser means no width/height, so the plot renders nothing -- and
        # this is reported as "silent" rather than looking like a success.
        assert ts.get_output("a_plot").status == "silent"
        assert ts.success is True

        ts.set_inputs(
            {
                ".clientdata_output_a_plot_width": 600,
                ".clientdata_output_a_plot_height": 400,
                ".clientdata_pixelratio": 1,
            }
        )
        rendered = ts.get_output("a_plot")
        assert rendered.status == "ok"
        assert sorted(rendered.value) == ["coordmap", "height", "src", "width"]
