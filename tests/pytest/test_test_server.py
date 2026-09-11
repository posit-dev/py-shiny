from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

import pytest

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny.testmode import export_test_values
from shiny.testserver import (
    AsyncTestServerScope,
    AsyncTestServerSession,
    TestServerScope,
    TestServerSession,
    TestServerValue,
    TestServerValues,
    test_server,
    test_server_async,
)
from shiny.testserver._test_server import DEFAULT_CLIENT_DATA, VALUE_FIELDS
from shiny.types import MISSING


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
        ts.set_inputs(n=25)
        assert ts.is_ok is True
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
        ts.set_inputs(n=25)
        assert ts.is_ok is True
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
        assert ts.is_ok is True
        # An output with no input dependency renders straight away.
        assert ts.get_output("greeting") == "express loaded"
        # There is no browser to report the slider's value, so `input.n()` raises
        # a silent exception and `doubled` renders nothing -- without failing.
        assert ts.get_output("doubled").status == "silent"
        # Silent is not an error: nothing rendered, nothing failed.
        assert ts.get_output("doubled").error is None

        ts.set_inputs(n=30)
        assert ts.is_ok is True
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
        ts.set_inputs(txt="pytest-sim")
        assert ts.is_ok is True
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
        assert ts.is_ok is False
        assert "Custom calculation error" in str(ts.get_output("err_out").error)


def test_test_server_initialization_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        raise RuntimeError("Fatal server init crash")

    app = App(app_ui, server)
    with test_server(app) as ts:
        assert ts.is_ok is False
        assert "Fatal server init crash" in str(ts.error)


def test_test_server_reactive_effect_error_is_failure():
    app_ui = ui.page_fluid(ui.output_text("out"))

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        def _():
            raise RuntimeError("Fatal effect crash")

    app = App(app_ui, server)
    with test_server(app) as ts:
        assert ts.is_ok is False
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
        assert ts.is_ok is True

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
    assert values.is_ok is True
    assert values.traceback is None

    # `to_values()` keeps the rich values; `dict(session)` converts all the way
    # down to plain data.
    assert sorted(as_dict) == sorted(VALUE_FIELDS)
    assert isinstance(values.outputs["out"], TestServerValue)
    assert as_dict["outputs"]["out"] == {
        "name": "out",
        "kind": "output",
        "status": "ok",
        "value": "simulated",
    }
    # Plain data all the way down means it survives a JSON round-trip.
    assert json.loads(json.dumps(as_dict)) == as_dict


def test_test_server_values_convert_to_a_dict_like_the_session():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def fine():
            return "hi"

        @render.text
        def never():
            return f"{input.n()}"

    with test_server(server) as ts:
        values = ts.to_values()

        # `dict(values)` is the snapshot equivalent of `dict(session)`.
        assert dict(values) == dict(ts)
        assert sorted(dict(values)) == sorted(VALUE_FIELDS)
        assert dict(values)["outputs"]["fine"]["value"] == "hi"
        assert "value" not in dict(values)["outputs"]["never"]

        with pytest.raises(KeyError):
            values["nope"]

    # The snapshot converts after the block too, since it holds copies.
    assert json.loads(json.dumps(dict(values))) == dict(values)
    # Reading the attribute keeps the rich value.
    assert isinstance(values.outputs["fine"], TestServerValue)


def test_test_server_dict_form_keys_on_status():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def fine():
            return "hi"

        @render.text
        def never():
            return f"{input.n()}"

        @render.text
        def boom():
            raise ValueError("kaboom")

    with test_server(server) as ts:
        outputs = dict(ts)["outputs"]

        # An item that produced no value has no `value` key at all, rather than
        # one holding `MISSING`.
        assert outputs["never"] == {
            "name": "never",
            "kind": "output",
            "status": "silent",
        }
        assert "value" not in outputs["never"]

        assert outputs["fine"]["value"] == "hi"
        assert "error" not in outputs["fine"]

        # An error carries what explains it, and still no `value`.
        assert outputs["boom"]["error"] == "kaboom"
        assert "ValueError: kaboom" in outputs["boom"]["traceback"]
        assert "value" not in outputs["boom"]

        # Asking a value for a key its status does not include is a KeyError.
        with pytest.raises(KeyError):
            ts.get_output("never")["value"]


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


def test_test_server_set_inputs_timeout_when_blocking():
    """
    A blocking effect holds the event loop, so `wait_for` cannot fire while it
    runs. The overrun is reported from the clock instead -- without that, whether
    the timeout or the completed flush won was a race, and CI lost it.
    """

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        def _():
            val = input.hang()
            if val is not None and val > 0:
                time.sleep(1.0)

    with test_server(server, timeout_secs=0.2) as s:
        with pytest.raises(TimeoutError, match="0.2s waiting for the reactive flush"):
            s.set_inputs(hang=1)


def test_test_server_set_inputs_timeout_when_awaiting():
    """An effect that awaits yields the loop, so `wait_for` fires normally."""

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.effect
        async def _():
            val = input.hang()
            if val is not None and val > 0:
                await asyncio.sleep(1.0)

    with test_server(server, timeout_secs=0.2) as s:
        with pytest.raises(TimeoutError, match="0.2s waiting for the reactive flush"):
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
    lambda ts: ts.is_ok,
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


def test_set_inputs_accepts_any_id():
    """
    `**kwargs` is the only channel, and it can carry any id.

    CPython does not require identifier keys when unpacking into `**kwargs`, and
    `self` is positional-only, so no id is unreachable.
    """

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def echo():
            values = (input.self(), input.kwargs(), input.n())
            return "|".join(str(v) for v in values)

        @render.text
        def ratio():
            return str(session.clientdata.pixelratio())

    with test_server(server) as ts:
        # `self` and `kwargs` would collide with the signature if not for `/`.
        ts.set_inputs(**{"self": 1, "kwargs": 2}, n=3)
        assert ts.get_output("echo") == "1|2|3"

        # Ids that are not valid identifiers -- client data starts with ".",
        # and a module namespaces with "-" -- go through the same channel. See
        # `test_test_server_reaches_a_module_through_its_namespaced_ids`.
        ts.set_inputs(**{".clientdata_pixelratio": 2})
        assert ts.get_output("ratio") == "2"


@pytest.mark.asyncio
async def test_async_set_inputs_accepts_ids_that_shadow_its_own_parameter():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def echo():
            return f"{input.self()}"

    async with test_server_async(server) as ts:
        await ts.set_inputs(**{"self": 5})
        assert ts.get_output("echo") == "5"


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
        assert ts.is_ok is True
        assert ts.get_export("tripled") == 15

        ts.set_inputs(val=-1)
        assert ts.is_ok is False
        assert "must be non-negative" in str(ts.get_output("checked").error)

        # The snapshot is rebuilt per flush, so a recovered output stops reporting
        # the stale error.
        ts.set_inputs(val=7)
        assert ts.is_ok is True
        assert ts.get_output("checked").error is None
        assert ts.get_output("checked").traceback is None
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
        "from shiny.testserver import test_server\n"
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


def test_test_server_value_rejects_incoherent_construction():
    # Frozen, so an instance that starts out incoherent stays that way.
    with pytest.raises(ValueError, match="`status` must be one of"):
        TestServerValue("x", "output", "missing")  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError, match="status 'error' needs an `error`"):
        TestServerValue("x", "output", "error")

    with pytest.raises(ValueError, match="may carry an `error`"):
        TestServerValue("x", "output", "ok", "v", error="bad")

    with pytest.raises(ValueError, match="status 'ok' needs a `value`"):
        TestServerValue("x", "output", "ok")

    with pytest.raises(ValueError, match="may carry a `value`"):
        TestServerValue("x", "output", "silent", "v")

    with pytest.raises(ValueError, match="no `error` cannot carry a `traceback`"):
        TestServerValue("x", "output", "silent", traceback="Traceback...")

    # An output that really did render `None` is still coherent, and is distinct
    # from one that produced nothing at all.
    assert TestServerValue("x", "output", "ok", None).value is None
    assert TestServerValue("x", "output", "silent").value is MISSING


def test_test_server_unknown_names_raise_rather_than_compare_unequal():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def real():
            return "hi"

    with test_server(server) as ts:
        # Without this, `!=` on a typo would quietly pass: a valueless item
        # compares unequal to everything.
        with pytest.raises(KeyError, match="No output named 'typo'"):
            assert ts.get_output("typo") != "hi"

        # The message names what is actually available.
        with pytest.raises(KeyError, match="Available: 'real'"):
            ts.get_output("typo")

        with pytest.raises(KeyError, match="No export named 'nope'. Available: none"):
            ts.get_export("nope")


def test_test_server_value_repr_shows_only_the_meaningful_field():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def fine():
            return "hi"

        @render.text
        def needs_input():
            return f"{input.n()}"

        @render.text
        def boom():
            raise ValueError("kaboom")

    with test_server(server) as ts:
        assert repr(ts.get_output("fine")) == (
            "TestServerValue('fine', kind='output', status='ok', value='hi')"
        )
        assert repr(ts.get_output("boom")) == (
            "TestServerValue('boom', kind='output', status='error', error='kaboom')"
        )
        # Neither field means anything for these, so neither is shown.
        assert repr(ts.get_output("needs_input")) == (
            "TestServerValue('needs_input', kind='output', status='silent')"
        )
        assert repr(TestServerValue("x", "output", "error", error="bad")) == (
            "TestServerValue('x', kind='output', status='error', error='bad')"
        )


def test_test_server_value_without_a_value_refuses_to_compare():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def needs_input():
            return f"{input.n()}"

        @render.text
        def boom():
            raise ValueError("kaboom")

    with test_server(server) as ts:
        silent = ts.get_output("needs_input")
        failed = ts.get_output("boom")
        assert silent.status == "silent"
        assert failed.status == "error"

        # Comparing against a value presumes there is one. Returning `False`
        # would answer a different question than the test is asking, and would
        # let every `!=` below pass while hiding why.
        for comparison in (
            lambda: silent == "5",
            lambda: silent != "5",
            lambda: silent == None,  # noqa: E711
            lambda: silent != None,  # noqa: E711
            lambda: silent in [None],  # pyright: ignore[reportUnnecessaryContains]
        ):
            with pytest.raises(ValueError, match="never rendered"):
                comparison()

        with pytest.raises(ValueError, match="raised, so there is no value"):
            assert failed != "anything"
        with pytest.raises(ValueError, match="kaboom"):
            assert failed == "anything"

        # Two rich values still compare structurally, without raising.
        assert silent == TestServerValue("needs_input", "output", "silent")
        assert silent != failed

        # And once it renders, the comparison answers normally.
        ts.set_inputs(n=5)
        assert ts.get_output("needs_input") == "5"

        # An output that really did render `None` still compares equal to it.
        ts.set_inputs(n=None)
        assert ts.get_output("needs_input").status == "ok"
        assert ts.get_output("needs_input") == "None"


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
        # There is no status for "does not exist"; the lookup fails instead, and
        # says what is actually there.
        with pytest.raises(KeyError, match="No output named 'no_such_output'"):
            ts.get_output("no_such_output")

        # A silent output is not a failure; an errored one is.
        assert ts.is_ok is False
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
        assert failed.traceback is not None
        assert "ValueError: kaboom" in failed.traceback
        assert "raise ValueError" in failed.traceback


def test_test_server_exposes_inputs():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def echo():
            return f"{input.a()}"

    with test_server(server) as ts:
        with pytest.raises(KeyError, match="No input named 'a'"):
            ts.get_input("a")

        ts.set_inputs(a=1, b="two")
        assert ts.get_input("a") == 1
        assert ts.get_input("b") == "two"
        assert ts.get_input("b").kind == "input"
        assert sorted(ts.to_values().inputs) == ["a", "b"]


def test_test_server_plot_renders_without_a_browser():
    plt = pytest.importorskip("matplotlib.pyplot")

    def server(input: Inputs, output: Outputs, session: Session):
        @render.plot
        def a_plot():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])
            return fig

    with test_server(server) as ts:
        # `render.plot` needs the size a browser would report. The session sends
        # stand-in values at startup, so a plot renders rather than going silent.
        rendered = ts.get_output("a_plot")
        assert rendered.status == "ok"
        assert sorted(rendered.value) == ["coordmap", "height", "src", "width"]
        # `width`/`height` here are the CSS sizes the client applies; the pixel
        # size the stand-ins drove is baked into the rendered `src` image.
        assert rendered.value["src"].startswith("data:image/png;base64,")

        # A test that cares about the size can still set it, which re-renders.
        ts.set_inputs(
            **{
                ".clientdata_output_a_plot_width": 300,
                ".clientdata_output_a_plot_height": 200,
            }
        )
        resized = ts.get_output("a_plot")
        assert resized.status == "ok"
        assert resized.value["src"] != rendered.value["src"]


def test_test_server_client_data_defaults_resolve():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def url():
            return session.clientdata.url_pathname()

        @render.text
        def ratio():
            return str(session.clientdata.pixelratio())

        @render.text
        def size():
            cd = session.clientdata
            return f"{cd.output_width('size')}x{cd.output_height('size')}"

    with test_server(server) as ts:
        # Without stand-ins each of these reads an unset input and goes silent.
        assert ts.get_output("url") == DEFAULT_CLIENT_DATA["url_pathname"]
        assert ts.get_output("ratio") == str(DEFAULT_CLIENT_DATA["pixelratio"])
        assert ts.get_output("size") == "{}x{}".format(
            DEFAULT_CLIENT_DATA["output_width"], DEFAULT_CLIENT_DATA["output_height"]
        )


@pytest.mark.parametrize("client_data", [None, {}])
def test_test_server_client_data_none_means_the_same_as_empty(
    client_data: dict[str, object] | None,
):
    """Neither suppresses the defaults; both mean "use all of them"."""

    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def url():
            return session.clientdata.url_pathname()

    with test_server(server, client_data=client_data) as ts:
        assert ts.get_output("url") == DEFAULT_CLIENT_DATA["url_pathname"]


def test_test_server_client_data_param_overrides_defaults():
    def server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def url():
            return session.clientdata.url_pathname()

        @render.text
        def size():
            cd = session.clientdata
            return f"{cd.output_width('size')}x{cd.output_height('size')}"

    with test_server(
        server,
        client_data={"url_pathname": "/dashboard", "output_width": 300},
    ) as ts:
        assert ts.get_output("url") == "/dashboard"
        # `output_*` applies to every output, and unset keys keep their default.
        assert ts.get_output("size") == "300x{}".format(
            DEFAULT_CLIENT_DATA["output_height"]
        )


def test_test_server_reaches_a_module_through_its_namespaced_ids():
    """The `"counter-n"` id form is what the docstring example documents."""

    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")

    with test_server(app_server) as ts:
        ts.set_inputs(**{"counter-n": 7})
        assert ts.get_output("counter-label") == "n=7"


EXPRESS_MODULE_APP_SRC = """from shiny.express import module, render, ui


@module
def counter(input, output, session):
    ui.input_numeric("n", "N", 0)

    @render.text
    def label():
        return f"n={input.n()}"


counter("counter")
"""


def test_test_server_make_scope_reads_a_module_with_bare_ids():
    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

        export_test_values(doubled=lambda: input.n() * 2)

    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")

        @render.text
        def app_level():
            return "outside the module"

    with test_server(app_server) as ts:
        counter = ts.make_scope("counter")
        assert isinstance(counter, TestServerScope)
        assert counter.ns == "counter"
        assert counter.root_scope() is ts

        # Bare ids in, bare ids out -- just like the module's own server code.
        assert counter.set_inputs(n=7) is counter
        assert counter.get_input("n") == 7
        assert counter.get_output("label") == "n=7"
        assert counter.get_export("doubled") == 14

        # The session still sees the namespaced form.
        assert ts.get_output("counter-label") == "n=7"

        # `to_values()` is scoped, and re-keyed by the bare id.
        values = counter.to_values()
        assert set(values.outputs) == {"label"}
        assert values.outputs["label"].name == "label"
        assert set(values.exports) == {"doubled"}
        assert "n" in values.inputs
        assert dict(counter)["outputs"]["label"]["value"] == "n=7"

        # The app-level output is outside the scope entirely.
        assert ts.get_output("app_level") == "outside the module"
        with pytest.raises(KeyError, match="No output named 'app_level'"):
            counter.get_output("app_level")


def test_test_server_scope_works_as_a_context_manager():
    """Entering a scope is a no-op; it only lets a module's block be indented."""

    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")

    with test_server(app_server) as ts:
        with ts.make_scope("counter") as counter:
            counter.set_inputs(n=7)
            assert counter.get_output("label") == "n=7"

        # Leaving the scope leaves the session -- and the scope -- untouched.
        assert ts.get_output("counter-label") == "n=7"
        assert counter.get_output("label") == "n=7"
        counter.set_inputs(n=8)
        assert ts.get_output("counter-label") == "n=8"


@pytest.mark.asyncio
async def test_test_server_async_scope_works_as_a_context_manager():
    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")

    async with test_server_async(app_server) as ts:
        async with ts.make_scope("counter") as counter:
            await counter.set_inputs(n=7)
            assert counter.get_output("label") == "n=7"

        assert ts.get_output("counter-label") == "n=7"
        await counter.set_inputs(n=8)
        assert ts.get_output("counter-label") == "n=8"


def test_test_server_scope_is_ok_covers_only_its_namespace():
    @module.server
    def boom_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            raise ValueError("kaboom")

    @module.server
    def fine_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return "fine"

    def app_server(input: Inputs, output: Outputs, session: Session):
        boom_server("bad")
        fine_server("good")

    with test_server(app_server) as ts:
        assert ts.is_ok is False

        assert ts.make_scope("bad").is_ok is False
        assert "label" in str(ts.make_scope("bad").error)

        # A sibling module's failure is not this module's problem.
        assert ts.make_scope("good").is_ok is True
        assert ts.make_scope("good").error is None


def test_test_server_scope_nests():
    @module.server
    def inner_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

    @module.server
    def outer_server(input: Inputs, output: Outputs, session: Session):
        inner_server("inner")

    def app_server(input: Inputs, output: Outputs, session: Session):
        outer_server("outer")

    with test_server(app_server) as ts:
        inner = ts.make_scope("outer").make_scope("inner")
        assert inner.ns == "outer-inner"
        inner.set_inputs(n=3)
        assert inner.get_output("label") == "n=3"
        assert ts.get_output("outer-inner-label") == "n=3"

        # An intermediate scope sees the nested id, minus its own prefix.
        assert ts.make_scope("outer").get_output("inner-label") == "n=3"


def test_test_server_scope_rejects_session_wide_ids():
    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")

    with test_server(app_server) as ts:
        # Client data belongs to the session, not to any one module, so
        # namespacing it would quietly produce an id nothing reads.
        with pytest.raises(ValueError, match="is session-wide"):
            ts.make_scope("counter").set_inputs(**{".clientdata_pixelratio": 2})


@pytest.mark.asyncio
async def test_test_server_async_make_scope():
    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"

    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")

    async with test_server_async(app_server) as ts:
        counter = ts.make_scope("counter")
        assert isinstance(counter, AsyncTestServerScope)
        assert counter.root_scope() is ts

        assert await counter.set_inputs(n=7) is counter
        assert counter.get_output("label") == "n=7"
        assert ts.get_output("counter-label") == "n=7"


def test_test_server_reaches_an_express_module(tmp_path: Path):
    """Express namespaces module ids the same way Core does."""
    app_file = tmp_path / "app.py"
    app_file.write_text(EXPRESS_MODULE_APP_SRC, encoding="utf-8")

    with test_server(app_file) as ts:
        ts.set_inputs(**{"counter-n": 7})
        assert ts.get_output("counter-label") == "n=7"


def _fixture_server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def doubled():
        return f"{input.n() * 2}"


@pytest.fixture
def documented_fixture():
    """The fixture pattern the docstring recommends, function-scoped."""
    with test_server(_fixture_server) as session:
        yield session


def test_fixture_pattern_works(documented_fixture: TestServerSession):
    documented_fixture.set_inputs(n=10)
    assert documented_fixture.get_output("doubled") == "20"


def test_fixture_pattern_is_isolated_between_tests(
    documented_fixture: TestServerSession,
):
    # A fresh session per test: `n` from the test above did not carry over.
    with pytest.raises(KeyError, match="No input named 'n'"):
        documented_fixture.get_input("n")


def test_captured_values_outlive_the_block():
    with test_server(_fixture_server) as ts:
        ts.set_inputs(n=10)
        values = ts.to_values()
        as_dict = dict(ts)

    assert values.outputs["doubled"].value == "20"
    assert as_dict["outputs"]["doubled"]["value"] == "20"
