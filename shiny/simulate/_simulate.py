from __future__ import annotations

import asyncio
import concurrent.futures
import json
import multiprocessing
import os
import sys
import tempfile
import time
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Any, Coroutine, Dict, Optional, TypeVar, Union, cast

from .._app import App
from .._connection import MockConnection
from ..express import is_express_app
from ..express._run import wrap_express_app
from ..reactive import isolate
from ..session import session_context
from ..session._session import AppSession

T = TypeVar("T")


@dataclass
class SimulationResult(Mapping[str, Any]):
    """Result of a Shiny headless reactive simulation."""

    success: bool
    error: Optional[str]
    traceback: str
    outputs: Dict[str, Any]
    errors: Dict[str, Any]
    exports: Dict[str, Any]
    rendered_ui: Optional[str]
    elapsed_ms: float = 0.0

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def __iter__(self):
        return iter(
            (
                "success",
                "error",
                "traceback",
                "outputs",
                "errors",
                "exports",
                "rendered_ui",
                "elapsed_ms",
            )
        )

    def __len__(self) -> int:
        return 8

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error": self.error,
            "traceback": self.traceback,
            "outputs": self.outputs,
            "errors": self.errors,
            "exports": self.exports,
            "rendered_ui": self.rendered_ui,
            "elapsed_ms": self.elapsed_ms,
        }


def _simulation_error_result(
    message: str, traceback_text: str = "", elapsed_ms: float = 0.0
) -> SimulationResult:
    return SimulationResult(
        success=False,
        error=message,
        traceback=traceback_text,
        outputs={},
        errors={},
        exports={},
        rendered_ui=None,
        elapsed_ms=elapsed_ms,
    )


async def _simulate_shiny_app_in_process(
    app: Optional[App] = None,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
) -> SimulationResult:
    start_t = time.perf_counter()
    old_testmode = os.environ.get("SHINY_TESTMODE")
    os.environ["SHINY_TESTMODE"] = "1"

    temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
    app_dir: Optional[str] = None
    try:
        app_obj: Optional[App] = None
        if app is not None and isinstance(app, App):
            app_obj = app
        elif code is not None:
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = Path(temp_dir.name) / "app.py"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)
            target_path = temp_path
            app_dir = str(target_path.parent)
            sys.path.insert(0, app_dir)
            if is_express_app(str(target_path), app_dir=None):
                app_obj = wrap_express_app(target_path)
            else:
                app_obj = _load_app_from_file(target_path)
        elif file_path is not None:
            target_path = Path(file_path).resolve()
            if not target_path.exists():
                return _simulation_error_result(f"File not found: {file_path}")
            app_dir = str(target_path.parent)
            sys.path.insert(0, app_dir)
            if is_express_app(str(target_path), app_dir=None):
                app_obj = wrap_express_app(target_path)
            else:
                app_obj = _load_app_from_file(target_path)
        else:
            return _simulation_error_result(
                "Either 'app', 'code', or 'file_path' must be provided."
            )

        if app_obj is None:
            return _simulation_error_result(
                "No Shiny 'App' instance found (expected 'app' or 'app_ui' + 'server')."
            )

        app_obj._test_mode = True
        conn = MockConnection()
        session: AppSession = app_obj._create_session(conn)

        initial_inputs = dict(inputs or {})

        async def driver():
            conn.cause_receive(json.dumps({"method": "init", "data": initial_inputs}))
            await asyncio.sleep(0.02)

            unhide_data: Dict[str, Any] = {}
            for out_name in session.output._outputs.keys():
                unhide_data[f".clientdata_output_{out_name}_hidden"] = False

            if unhide_data:
                conn.cause_receive(
                    json.dumps({"method": "update", "data": unhide_data})
                )
                await asyncio.sleep(0.02)

            conn.cause_disconnect()

        try:
            await asyncio.gather(driver(), session._run())
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return _simulation_error_result(
                f"Runtime error during session execution: {type(e).__name__}: {e}",
                traceback.format_exc(),
                elapsed_ms=elapsed_ms,
            )

        outputs = dict(session._outbound_message_queues.test_values)
        errors = dict(session._outbound_message_queues.test_errors)
        exports: Dict[str, Any] = {}
        raw_exports: Any = getattr(session, "_test_value_exports", None) or getattr(
            session, "_test_values", None
        )
        if isinstance(raw_exports, dict):
            typed_exports = cast(Dict[str, Any], raw_exports)
            with session_context(session):
                with isolate():
                    for k, fn in typed_exports.items():
                        try:
                            fn_obj = cast(object, fn)
                            exports[k] = fn() if callable(fn_obj) else fn
                        except Exception as e:
                            exports[k] = f"<Error evaluating export {k}: {e}>"

        rendered_ui: Optional[str] = None
        rendered_attr = getattr(app_obj, "_rendered_ui", None)
        if rendered_attr is not None:
            try:
                rendered_ui = str(rendered_attr)
            except Exception:
                pass

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return SimulationResult(
            success=len(errors) == 0,
            error=(
                None
                if len(errors) == 0
                else f"{len(errors)} reactive error(s) occurred"
            ),
            traceback="",
            outputs=outputs,
            errors=errors,
            exports=exports,
            rendered_ui=rendered_ui,
            elapsed_ms=elapsed_ms,
        )

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return _simulation_error_result(
            f"Failed during app load: {type(e).__name__}: {e}",
            traceback.format_exc(),
            elapsed_ms=elapsed_ms,
        )
    finally:
        if app_dir is not None:
            try:
                sys.path.remove(app_dir)
            except ValueError:
                pass

        if old_testmode is None:
            os.environ.pop("SHINY_TESTMODE", None)
        else:
            os.environ["SHINY_TESTMODE"] = old_testmode

        if temp_dir is not None:
            try:
                temp_dir.cleanup()
            except Exception:
                pass


def _load_app_from_file(target_path: Path) -> Optional[App]:
    module_name = f"_shiny_sim_{target_path.stem.replace('.', '_')}_{id(target_path)}"
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, target_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {target_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    if hasattr(mod, "app") and isinstance(mod.app, App):
        return mod.app
    elif hasattr(mod, "app_ui") and hasattr(mod, "server"):
        return App(mod.app_ui, mod.server)
    else:
        for val in mod.__dict__.values():
            if isinstance(val, App):
                return val
    return None


def _simulation_worker(
    connection: Connection,
    code: Optional[str],
    file_path: Optional[str],
    inputs: Optional[Dict[str, Any]],
) -> None:
    try:
        result = asyncio.run(
            _simulate_shiny_app_in_process(
                app=None,
                code=code,
                file_path=file_path,
                inputs=inputs,
            )
        )
        connection.send(result.to_dict())
    except Exception as e:
        connection.send(
            _simulation_error_result(
                f"Simulation worker failed: {type(e).__name__}: {e}",
                traceback.format_exc(),
            ).to_dict()
        )
    finally:
        connection.close()


async def _simulate_in_subprocess(
    code: Optional[str] = None,
    file_path: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    timeout_secs: float = 3.0,
) -> SimulationResult:
    start_t = time.perf_counter()
    context = multiprocessing.get_context("spawn")
    receive_connection, send_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=_simulation_worker,
        args=(send_connection, code, file_path, inputs),
    )
    process.start()
    send_connection.close()

    try:
        has_result = await asyncio.to_thread(receive_connection.poll, timeout_secs)
        if not has_result:
            process.terminate()
            await asyncio.to_thread(process.join, 1.0)
            if process.is_alive():
                process.kill()
                await asyncio.to_thread(process.join)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return _simulation_error_result(
                f"Simulation timed out after {timeout_secs}s; the worker process was terminated.",
                elapsed_ms=elapsed_ms,
            )

        try:
            raw_result = cast(Dict[str, Any], receive_connection.recv())
        except EOFError:
            await asyncio.to_thread(process.join)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return _simulation_error_result(
                f"Simulation worker exited with code {process.exitcode} without returning a result.",
                elapsed_ms=elapsed_ms,
            )

        await asyncio.to_thread(process.join)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return SimulationResult(
            success=raw_result.get("success", False),
            error=raw_result.get("error"),
            traceback=raw_result.get("traceback", ""),
            outputs=raw_result.get("outputs", {}),
            errors=raw_result.get("errors", {}),
            exports=raw_result.get("exports", {}),
            rendered_ui=raw_result.get("rendered_ui"),
            elapsed_ms=raw_result.get("elapsed_ms", elapsed_ms),
        )
    finally:
        receive_connection.close()
        if process.is_alive():
            process.terminate()
            await asyncio.to_thread(process.join)
        process.close()


def _run_coroutine_sync(coro: Coroutine[Any, Any, T], timeout_secs: float) -> T:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result(timeout=timeout_secs + 1.0)
    else:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout_secs + 1.0))


async def simulate_async(
    app: Union[App, str, Path, None] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 3.0,
    in_process: Optional[bool] = None,
) -> SimulationResult:
    """Asynchronously simulate a Shiny app in-memory without a browser."""
    resolved_app: Optional[App] = None
    resolved_code: Optional[str] = code
    resolved_path: Optional[Union[str, Path]] = file_path

    if isinstance(app, App):
        resolved_app = app
    elif isinstance(app, Path):
        resolved_path = app
    elif isinstance(app, str):
        if "\n" in app or "from shiny" in app or "import shiny" in app:
            resolved_code = app
        else:
            resolved_path = app

    use_in_process = in_process if in_process is not None else True

    if use_in_process or resolved_app is not None:
        return await _simulate_shiny_app_in_process(
            app=resolved_app,
            code=resolved_code,
            file_path=resolved_path,
            inputs=inputs,
        )
    else:
        path_str = str(resolved_path) if resolved_path is not None else None
        inputs_dict = dict(inputs) if inputs is not None else None
        return await _simulate_in_subprocess(
            code=resolved_code,
            file_path=path_str,
            inputs=inputs_dict,
            timeout_secs=timeout_secs,
        )


def simulate(
    app: Union[App, str, Path, None] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 3.0,
    in_process: Optional[bool] = None,
) -> SimulationResult:
    """Simulate a Shiny app in-memory without a browser for testing."""
    coro = simulate_async(
        app=app,
        code=code,
        file_path=file_path,
        inputs=inputs,
        timeout_secs=timeout_secs,
        in_process=in_process,
    )
    return _run_coroutine_sync(coro, timeout_secs=timeout_secs)


simulate_app = simulate
simulate_shiny_app = simulate_async
