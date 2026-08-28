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
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from .._app import App
from .._connection import MockConnection
from ..express import is_express_app
from ..express._run import wrap_express_app
from ..session._session import AppSession
from ..ui import page_fluid

T = TypeVar("T")


@dataclass
class TestServerResult(Mapping[str, Any]):
    __test__ = False

    success: bool
    error: Optional[str]
    traceback: str
    outputs: Dict[str, Any]
    errors: Dict[str, Any]
    exports: Dict[str, Any]
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
                "elapsed_ms",
            )
        )

    def __len__(self) -> int:
        return 7

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
            "elapsed_ms": self.elapsed_ms,
        }


def _error_result(
    message: str, traceback_text: str = "", elapsed_ms: float = 0.0
) -> TestServerResult:
    return TestServerResult(
        success=False,
        error=message,
        traceback=traceback_text,
        outputs={},
        errors={"__fatal__": message},
        exports={},
        elapsed_ms=elapsed_ms,
    )


async def _test_server_in_process(
    app: Optional[Union[App, Callable[..., Any]]] = None,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
) -> TestServerResult:
    start_t = time.perf_counter()
    old_testmode = os.environ.get("SHINY_TESTMODE")
    os.environ["SHINY_TESTMODE"] = "1"

    temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
    app_dir: Optional[str] = None
    saved_sys_path = list(sys.path)
    app_obj: Optional[App] = None
    old_app_test_mode: Optional[bool] = None
    old_app_server: Optional[Callable[..., Any]] = None

    try:
        if app is not None:
            if isinstance(app, App):
                app_obj = app
            elif callable(app):
                app_obj = App(page_fluid(), app)
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
                return _error_result(f"File not found: {file_path}")
            app_dir = str(target_path.parent)
            sys.path.insert(0, app_dir)
            if is_express_app(str(target_path), app_dir=None):
                app_obj = wrap_express_app(target_path)
            else:
                app_obj = _load_app_from_file(target_path)
        else:
            return _error_result(
                "Either 'app', 'code', or 'file_path' must be provided."
            )

        if app_obj is None:
            return _error_result(
                "No Shiny 'App' instance found (expected 'app' or 'app_ui' + 'server')."
            )

        old_app_test_mode = getattr(app_obj, "_test_mode", None)
        app_obj._test_mode = True

        conn = MockConnection()
        session: AppSession = app_obj._create_session(conn)

        fatal_errors: List[Tuple[Exception, str]] = []

        orig_unhandled_error = session._unhandled_error

        async def custom_unhandled_error(e: Exception) -> None:
            fatal_errors.append((e, traceback.format_exc()))
            await orig_unhandled_error(e)

        session._unhandled_error = custom_unhandled_error

        orig_print_error = session._print_error_message

        def custom_print_error(message: str | Exception) -> None:
            if isinstance(message, Exception):
                fatal_errors.append((message, traceback.format_exc()))
            else:
                fatal_errors.append((RuntimeError(str(message)), str(message)))
            orig_print_error(message)

        session._print_error_message = (
            custom_print_error  # pyright: ignore[reportAttributeAccessIssue]
        )

        old_app_server = app_obj.server
        orig_server = old_app_server

        def wrapped_server(input: Any, output: Any, session: Any) -> Any:
            try:
                return orig_server(input, output, session)
            except Exception as e:
                fatal_errors.append((e, traceback.format_exc()))
                raise

        app_obj.server = wrapped_server

        initial_inputs = dict(inputs or {})

        async def on_initial_flush() -> None:
            unhide_data: Dict[str, Any] = {}
            for out_name in session.output._outputs.keys():
                unhide_data[f".clientdata_output_{out_name}_hidden"] = False
            if unhide_data:
                conn.cause_receive(
                    json.dumps({"method": "update", "data": unhide_data})
                )
            conn.cause_disconnect()

        session.on_flushed(on_initial_flush, once=True)

        conn.cause_receive(json.dumps({"method": "init", "data": initial_inputs}))

        try:
            await session._run()
        except Exception as e:
            fatal_errors.append((e, traceback.format_exc()))
        finally:
            conn.cause_disconnect()

        snapshot = await session._build_test_snapshot()
        outputs: Dict[str, Any] = snapshot.get("output", {})
        exports: Dict[str, Any] = snapshot.get("export", {})
        errors: Dict[str, Any] = dict(session._outbound_message_queues.test_errors)

        for key, val in list(outputs.items()):
            if isinstance(val, dict):
                val_dict = cast(Dict[str, Any], val)
                if "__shiny_output_error__" in val_dict:
                    errors[key] = val_dict["__shiny_output_error__"]
                elif "__shiny_snapshot_preprocess_error__" in val_dict:
                    errors[key] = val_dict["__shiny_snapshot_preprocess_error__"]

        for key, val in list(exports.items()):
            if isinstance(val, dict):
                val_dict = cast(Dict[str, Any], val)
                if "__shiny_serialization_error__" in val_dict:
                    errors[f"export:{key}"] = val_dict["__shiny_serialization_error__"]

        if fatal_errors:
            first_exc, first_tb = fatal_errors[0]
            errors["__fatal__"] = str(first_exc)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return TestServerResult(
                success=False,
                error=f"Session fatal error: {type(first_exc).__name__}: {first_exc}",
                traceback=first_tb,
                outputs=outputs,
                errors=errors,
                exports=exports,
                elapsed_ms=elapsed_ms,
            )

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        success = len(errors) == 0
        error_msg = None if success else f"{len(errors)} reactive error(s) occurred"

        return TestServerResult(
            success=success,
            error=error_msg,
            traceback="",
            outputs=outputs,
            errors=errors,
            exports=exports,
            elapsed_ms=elapsed_ms,
        )

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return _error_result(
            f"Failed to test server: {e}",
            traceback.format_exc(),
            elapsed_ms=elapsed_ms,
        )
    finally:
        sys.path = saved_sys_path
        if old_testmode is None:
            os.environ.pop("SHINY_TESTMODE", None)
        else:
            os.environ["SHINY_TESTMODE"] = old_testmode
        if temp_dir is not None:
            temp_dir.cleanup()
        if app_obj is not None:
            if old_app_test_mode is not None:
                app_obj._test_mode = old_app_test_mode
            if old_app_server is not None:
                app_obj.server = old_app_server


def _load_app_from_file(target_path: Path) -> Optional[App]:
    import importlib.util

    module_name = f"_test_server_app_{target_path.stem}_{abs(hash(str(target_path)))}"
    spec = importlib.util.spec_from_file_location(module_name, target_path)
    if spec is None or spec.loader is None:
        return None

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        raise

    app_candidate = getattr(mod, "app", None)
    if isinstance(app_candidate, App):
        return app_candidate

    app_ui = getattr(mod, "app_ui", None)
    server = getattr(mod, "server", None)
    if app_ui is not None and server is not None:
        return App(app_ui, server)

    return None


def _subprocess_test_server_worker(
    pipe: Connection,
    code: Optional[str],
    file_path: Optional[str],
    inputs: Optional[Dict[str, Any]],
) -> None:
    try:
        res = _run_coroutine_sync(
            _test_server_in_process(
                code=code,
                file_path=file_path,
                inputs=inputs,
            ),
            timeout_secs=300.0,
        )
        pipe.send(res.to_dict())
    except Exception as e:
        err_res = _error_result(
            f"Subprocess worker crashed: {e}", traceback.format_exc()
        )
        pipe.send(err_res.to_dict())
    finally:
        pipe.close()


async def _test_server_subprocess(
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 3.0,
) -> TestServerResult:
    start_t = time.perf_counter()
    ctx = multiprocessing.get_context("spawn")
    parent_conn, child_conn = ctx.Pipe()

    str_path = str(Path(file_path).resolve()) if file_path is not None else None
    dict_inputs = dict(inputs or {})

    proc = ctx.Process(
        target=_subprocess_test_server_worker,
        args=(child_conn, code, str_path, dict_inputs),
    )
    proc.start()
    child_conn.close()

    loop = asyncio.get_running_loop()

    def read_from_process() -> Optional[Dict[str, Any]]:
        has_data = False
        try:
            has_data = parent_conn.poll(timeout=timeout_secs)
        except Exception:
            pass

        if has_data:
            try:
                data = parent_conn.recv()
                proc.join(timeout=1.0)
                return cast(Dict[str, Any], data)
            except EOFError:
                proc.join(timeout=1.0)
                raise RuntimeError(
                    f"Test server worker process exited with code {proc.exitcode} without returning a result"
                )

        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=0.5)
            if proc.is_alive():
                proc.kill()
                proc.join()
            return None
        else:
            proc.join(timeout=0.5)
            raise RuntimeError(
                f"Test server worker process exited with code {proc.exitcode} without returning a result"
            )

    try:
        data = await loop.run_in_executor(None, read_from_process)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        if data is None:
            return _error_result(
                f"Test server timed out after {timeout_secs}s",
                elapsed_ms=elapsed_ms,
            )

        return TestServerResult(
            success=data["success"],
            error=data["error"],
            traceback=data.get("traceback", ""),
            outputs=data.get("outputs", {}),
            errors=data.get("errors", {}),
            exports=data.get("exports", {}),
            elapsed_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return _error_result(
            f"Process error: {e}",
            traceback.format_exc(),
            elapsed_ms=elapsed_ms,
        )
    finally:
        parent_conn.close()


def _run_coroutine_sync(
    coro: Coroutine[Any, Any, TestServerResult], timeout_secs: float
) -> TestServerResult:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    try:
        if loop is not None and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result(timeout=timeout_secs + 2.0)
        else:
            return asyncio.run(coro)
    except (asyncio.TimeoutError, concurrent.futures.TimeoutError):
        return _error_result(f"Test server timed out after {timeout_secs}s")


def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 3.0,
    in_process: Optional[bool] = None,
) -> TestServerResult:
    return _run_coroutine_sync(
        test_server_async(
            app=app,
            code=code,
            file_path=file_path,
            inputs=inputs,
            timeout_secs=timeout_secs,
            in_process=in_process,
        ),
        timeout_secs=timeout_secs,
    )


async def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 3.0,
    in_process: Optional[bool] = None,
) -> TestServerResult:
    target_app: Optional[Union[App, Callable[..., Any]]] = None
    target_path: Optional[Union[str, Path]] = file_path
    target_code: Optional[str] = code

    if app is not None:
        if isinstance(app, App) or callable(app):
            target_app = app
        elif isinstance(app, (str, Path)):
            target_path = app

    use_in_process: bool
    if in_process is not None:
        use_in_process = in_process
    else:
        use_in_process = target_app is not None

    try:
        if use_in_process:
            return await asyncio.wait_for(
                _test_server_in_process(
                    app=target_app,
                    code=target_code,
                    file_path=target_path,
                    inputs=inputs,
                ),
                timeout=timeout_secs,
            )
        else:
            return await _test_server_subprocess(
                code=target_code,
                file_path=target_path,
                inputs=inputs,
                timeout_secs=timeout_secs,
            )
    except asyncio.TimeoutError:
        return _error_result(f"Test server timed out after {timeout_secs}s")


test_server.__test__ = False  # pyright: ignore[reportFunctionMemberAccess]
test_server_async.__test__ = False  # pyright: ignore[reportFunctionMemberAccess]
