from __future__ import annotations

import asyncio
import inspect
import json
import os
import sys
import tempfile
import threading
import time
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
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


class AsyncTestServerSession:
    __test__ = False

    def __init__(
        self,
        app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
        *,
        code: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        inputs: Optional[Mapping[str, Any]] = None,
        timeout_secs: float = 5.0,
    ) -> None:
        self._target_app = app
        self._target_code = code
        self._target_path = file_path
        self._initial_inputs = dict(inputs or {})
        self._timeout_secs = timeout_secs

        self._app_obj: Optional[App] = None
        self._session: Optional[AppSession] = None
        self._conn: Optional[MockConnection] = None
        self._session_task: Optional[asyncio.Task[None]] = None
        self._temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        self._saved_sys_path: Optional[List[str]] = None
        self._saved_modules: Optional[Set[str]] = None
        self._old_testmode: Optional[str] = None
        self._old_app_test_mode: Optional[bool] = None
        self._old_app_server: Optional[Callable[..., Any]] = None
        self._fatal_errors: List[Tuple[Exception, str]] = []
        self._current_outputs: Dict[str, Any] = {}
        self._current_exports: Dict[str, Any] = {}
        self._current_errors: Dict[str, Any] = {}
        self._is_started: bool = False
        self._start_time: float = 0.0

    async def _cleanup(self) -> None:
        if self._conn is not None:
            self._conn.cause_disconnect()
        if self._session_task is not None:
            try:
                await asyncio.wait_for(self._session_task, timeout=2.0)
            except Exception:
                pass
            self._session_task = None

        if self._saved_sys_path is not None:
            sys.path[:] = self._saved_sys_path
            self._saved_sys_path = None

        if self._saved_modules is not None:
            new_modules = set(sys.modules.keys()) - self._saved_modules
            for mod_name in new_modules:
                sys.modules.pop(mod_name, None)
            self._saved_modules = None

        if self._old_testmode is not None:
            os.environ["SHINY_TESTMODE"] = self._old_testmode
            self._old_testmode = None
        else:
            os.environ.pop("SHINY_TESTMODE", None)

        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None

        if self._app_obj is not None:
            if self._old_app_test_mode is not None:
                self._app_obj._test_mode = self._old_app_test_mode
                self._old_app_test_mode = None
            if self._old_app_server is not None:
                self._app_obj.server = self._old_app_server
                self._old_app_server = None

    async def start(self) -> AsyncTestServerSession:
        try:
            return await self._start_impl()
        except Exception:
            await self._cleanup()
            raise

    async def _start_impl(self) -> AsyncTestServerSession:
        self._start_time = time.perf_counter()
        self._old_testmode = os.environ.get("SHINY_TESTMODE")
        os.environ["SHINY_TESTMODE"] = "1"
        self._saved_sys_path = list(sys.path)
        self._saved_modules = set(sys.modules.keys())

        if self._target_app is not None:
            if isinstance(self._target_app, App):
                self._app_obj = self._target_app
            elif callable(self._target_app):
                self._app_obj = App(page_fluid(), self._target_app)
            elif isinstance(self._target_app, (str, Path)):
                target_path = Path(self._target_app).resolve()
                if not target_path.exists():
                    raise FileNotFoundError(f"File not found: {self._target_app}")
                app_dir = str(target_path.parent)
                sys.path.insert(0, app_dir)
                if is_express_app(str(target_path), app_dir=None):
                    self._app_obj = wrap_express_app(target_path)
                else:
                    self._app_obj = _load_app_from_file(target_path)
        elif self._target_code is not None:
            self._temp_dir = tempfile.TemporaryDirectory()
            temp_path = Path(self._temp_dir.name) / "app.py"
            temp_path.write_text(self._target_code, encoding="utf-8")
            app_dir = str(temp_path.parent)
            sys.path.insert(0, app_dir)
            if is_express_app(str(temp_path), app_dir=None):
                self._app_obj = wrap_express_app(temp_path)
            else:
                self._app_obj = _load_app_from_file(temp_path)
        elif self._target_path is not None:
            target_path = Path(self._target_path).resolve()
            if not target_path.exists():
                raise FileNotFoundError(f"File not found: {self._target_path}")
            app_dir = str(target_path.parent)
            sys.path.insert(0, app_dir)
            if is_express_app(str(target_path), app_dir=None):
                self._app_obj = wrap_express_app(target_path)
            else:
                self._app_obj = _load_app_from_file(target_path)
        else:
            raise ValueError("Either 'app', 'code', or 'file_path' must be provided.")

        if self._app_obj is None:
            raise RuntimeError("No Shiny 'App' instance found.")

        self._old_app_test_mode = getattr(self._app_obj, "_test_mode", None)
        self._app_obj._test_mode = True

        self._conn = MockConnection()
        self._session = self._app_obj._create_session(self._conn)

        initial_flush_done = asyncio.Event()
        unhide_flush_done = asyncio.Event()

        orig_unhandled_error = self._session._unhandled_error

        async def custom_unhandled_error(e: Exception) -> None:
            self._fatal_errors.append((e, traceback.format_exc()))
            initial_flush_done.set()
            unhide_flush_done.set()
            await orig_unhandled_error(e)

        self._session._unhandled_error = custom_unhandled_error

        orig_print_error = self._session._print_error_message

        def custom_print_error(message: str | Exception) -> None:
            if isinstance(message, Exception):
                self._fatal_errors.append((message, traceback.format_exc()))
            else:
                self._fatal_errors.append((RuntimeError(str(message)), str(message)))
            initial_flush_done.set()
            unhide_flush_done.set()
            orig_print_error(message)

        self._session._print_error_message = (
            custom_print_error  # pyright: ignore[reportAttributeAccessIssue]
        )

        self._old_app_server = self._app_obj.server
        orig_server = self._old_app_server

        def wrapped_server(input: Any, output: Any, session: Any) -> Any:
            try:
                return orig_server(input, output, session)
            except Exception as e:
                self._fatal_errors.append((e, traceback.format_exc()))
                initial_flush_done.set()
                unhide_flush_done.set()
                raise

        self._app_obj.server = wrapped_server

        async def unhide_all_outputs() -> None:
            if self._session is None or self._conn is None:
                initial_flush_done.set()
                unhide_flush_done.set()
                return

            unhide_data: Dict[str, Any] = {}
            for out_name in self._session.output._outputs.keys():
                unhide_data[f".clientdata_output_{out_name}_hidden"] = False

            if unhide_data:

                def on_unhide_flushed() -> None:
                    unhide_flush_done.set()

                self._session.on_flushed(on_unhide_flushed, once=True)
                self._conn.cause_receive(
                    json.dumps({"method": "update", "data": unhide_data})
                )
            else:
                unhide_flush_done.set()

            initial_flush_done.set()

        self._session.on_flushed(unhide_all_outputs, once=True)

        self._session_task = asyncio.create_task(self._session._run())

        def on_session_task_done(_: asyncio.Task[None]) -> None:
            initial_flush_done.set()
            unhide_flush_done.set()

        self._session_task.add_done_callback(on_session_task_done)

        self._conn.cause_receive(
            json.dumps({"method": "init", "data": self._initial_inputs})
        )

        self._is_started = True

        deadline = time.monotonic() + self._timeout_secs

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s during session initialization."
            )
        try:
            await asyncio.wait_for(initial_flush_done.wait(), timeout=remaining)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s waiting for initial flush."
            )

        if not self._fatal_errors and not self._session_task.done():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"test_server timed out after {self._timeout_secs}s during session initialization."
                )
            try:
                await asyncio.wait_for(unhide_flush_done.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"test_server timed out after {self._timeout_secs}s waiting for output initialization."
                )

        await asyncio.sleep(0.01)
        await self._refresh_snapshots()
        return self

    async def _refresh_snapshots(self) -> None:
        if self._session is None:
            return
        snapshot = await self._session._build_test_snapshot()
        self._current_outputs = snapshot.get("output", {})
        self._current_exports = snapshot.get("export", {})
        self._current_errors = dict(self._session._outbound_message_queues.test_errors)

        for key, val in list(self._current_outputs.items()):
            if isinstance(val, dict):
                val_dict = cast(Dict[str, Any], val)
                if "__shiny_output_error__" in val_dict:
                    self._current_errors[key] = val_dict["__shiny_output_error__"]
                elif "__shiny_snapshot_preprocess_error__" in val_dict:
                    self._current_errors[key] = val_dict[
                        "__shiny_snapshot_preprocess_error__"
                    ]

        for key, val in list(self._current_exports.items()):
            if isinstance(val, dict):
                val_dict = cast(Dict[str, Any], val)
                if "__shiny_serialization_error__" in val_dict:
                    self._current_errors[f"export:{key}"] = val_dict[
                        "__shiny_serialization_error__"
                    ]

        if self._fatal_errors:
            first_exc, _ = self._fatal_errors[0]
            self._current_errors["__fatal__"] = str(first_exc)

    async def set_inputs(
        self, inputs: Optional[Mapping[str, Any]] = None, **kwargs: Any
    ) -> None:
        all_inputs: Dict[str, Any] = {}
        if inputs:
            for k, v in inputs.items():
                all_inputs[str(k)] = v
        for k, v in kwargs.items():
            all_inputs[k] = v

        if self._conn is None or self._session is None:
            raise RuntimeError("Session is not running.")

        flush_done = asyncio.Event()
        unreg: Optional[Callable[[], None]] = None

        def on_set_inputs_flushed() -> None:
            flush_done.set()

        unreg = self._session.on_flushed(on_set_inputs_flushed, once=False)
        self._conn.cause_receive(json.dumps({"method": "update", "data": all_inputs}))
        try:
            await asyncio.wait_for(flush_done.wait(), timeout=self._timeout_secs)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s waiting for reactive flush following set_inputs()."
            )
        finally:
            if unreg is not None:
                try:
                    unreg()
                except Exception:
                    pass

        await asyncio.sleep(0.01)
        await self._refresh_snapshots()

    async def flush(self) -> None:
        await self._refresh_snapshots()

    @property
    def outputs(self) -> Dict[str, Any]:
        return dict(self._current_outputs)

    @property
    def exports(self) -> Dict[str, Any]:
        return dict(self._current_exports)

    @property
    def errors(self) -> Dict[str, Any]:
        return dict(self._current_errors)

    @property
    def success(self) -> bool:
        return len(self._current_errors) == 0 and len(self._fatal_errors) == 0

    @property
    def error(self) -> Optional[str]:
        if self._fatal_errors:
            first_exc, _ = self._fatal_errors[0]
            return f"Session fatal error: {type(first_exc).__name__}: {first_exc}"
        if len(self._current_errors) > 0:
            return f"{len(self._current_errors)} reactive error(s) occurred"
        return None

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start_time) * 1000.0

    def get_output(self, name: str, default: Any = None) -> Any:
        return self._current_outputs.get(name, default)

    def get_export(self, name: str, default: Any = None) -> Any:
        return self._current_exports.get(name, default)

    def to_result(self) -> TestServerResult:
        first_tb = self._fatal_errors[0][1] if self._fatal_errors else ""
        return TestServerResult(
            success=self.success,
            error=self.error,
            traceback=first_tb,
            outputs=self.outputs,
            errors=self.errors,
            exports=self.exports,
            elapsed_ms=self.elapsed_ms,
        )

    async def close(self) -> None:
        self._is_started = False
        await self._cleanup()

    async def __aenter__(self) -> AsyncTestServerSession:
        return await self.start()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()


class TestServerSession(Mapping[str, Any]):
    __test__ = False

    def __init__(
        self,
        app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
        *,
        code: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        inputs: Optional[Mapping[str, Any]] = None,
        timeout_secs: float = 5.0,
    ) -> None:
        self._async_session = AsyncTestServerSession(
            app=app,
            code=code,
            file_path=file_path,
            inputs=inputs,
            timeout_secs=timeout_secs,
        )
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._timeout_secs = timeout_secs
        self._is_running = False
        self._entered = False
        self._cached_result: Optional[TestServerResult] = None

    def start(self) -> TestServerSession:
        if self._is_running:
            return self
        ready_event = threading.Event()
        start_error: List[Exception] = []

        def runner():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._stop_event = asyncio.Event()

            async def _init_and_run():
                try:
                    await self._async_session.start()
                    ready_event.set()
                except Exception as e:
                    start_error.append(e)
                    ready_event.set()
                    return

                if self._stop_event is not None:
                    await self._stop_event.wait()
                await self._async_session.close()

            try:
                self._loop.run_until_complete(_init_and_run())
            finally:
                pending = [t for t in asyncio.all_tasks(self._loop) if not t.done()]
                for t in pending:
                    t.cancel()
                if pending:
                    self._loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                self._loop.close()

        self._is_running = True
        self._thread = threading.Thread(target=runner, daemon=True)
        self._thread.start()

        if not ready_event.wait(timeout=self._timeout_secs):
            self.close()
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s during startup."
            )
        if start_error:
            self.close()
            raise start_error[0]
        return self

    def set_inputs(
        self, inputs: Optional[Mapping[str, Any]] = None, **kwargs: Any
    ) -> None:
        if not self._is_running or self._loop is None:
            self.start()
        if self._loop is None:
            raise RuntimeError("Event loop not initialized.")
        future = asyncio.run_coroutine_threadsafe(
            self._async_session.set_inputs(inputs=inputs, **kwargs),
            self._loop,
        )
        future.result(timeout=self._timeout_secs)

    def flush(self) -> None:
        if self._loop is not None and self._is_running:
            future = asyncio.run_coroutine_threadsafe(
                self._async_session.flush(),
                self._loop,
            )
            future.result(timeout=self._timeout_secs)

    def _ensure_run_once(self) -> None:
        if not self._is_running and self._cached_result is None:
            self.start()
            self._cached_result = self._async_session.to_result()
            self.close()

    @property
    def outputs(self) -> Dict[str, Any]:
        if self._is_running:
            return self._async_session.outputs
        self._ensure_run_once()
        return self._cached_result.outputs if self._cached_result else {}

    @property
    def exports(self) -> Dict[str, Any]:
        if self._is_running:
            return self._async_session.exports
        self._ensure_run_once()
        return self._cached_result.exports if self._cached_result else {}

    @property
    def errors(self) -> Dict[str, Any]:
        if self._is_running:
            return self._async_session.errors
        self._ensure_run_once()
        return self._cached_result.errors if self._cached_result else {}

    @property
    def success(self) -> bool:
        if self._is_running:
            return self._async_session.success
        self._ensure_run_once()
        return self._cached_result.success if self._cached_result else False

    @property
    def error(self) -> Optional[str]:
        if self._is_running:
            return self._async_session.error
        self._ensure_run_once()
        return self._cached_result.error if self._cached_result else None

    @property
    def traceback(self) -> str:
        if self._is_running:
            return (
                self._async_session._fatal_errors[0][1]
                if self._async_session._fatal_errors
                else ""
            )
        self._ensure_run_once()
        return self._cached_result.traceback if self._cached_result else ""

    @property
    def elapsed_ms(self) -> float:
        if self._is_running:
            return self._async_session.elapsed_ms
        self._ensure_run_once()
        return self._cached_result.elapsed_ms if self._cached_result else 0.0

    def get_output(self, name: str, default: Any = None) -> Any:
        return self.outputs.get(name, default)

    def get_export(self, name: str, default: Any = None) -> Any:
        return self.exports.get(name, default)

    def to_result(self) -> TestServerResult:
        if self._is_running:
            return self._async_session.to_result()
        self._ensure_run_once()
        return self._cached_result or _error_result("No result")

    def to_dict(self) -> Dict[str, Any]:
        return self.to_result().to_dict()

    def __getitem__(self, key: str) -> Any:
        res = self.to_result()
        return res[key]

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
        res = self.to_result()
        return res.get(key, default)

    def close(self) -> None:
        if not self._is_running:
            return
        self._is_running = False
        if (
            self._loop is not None
            and self._loop.is_running()
            and self._stop_event is not None
        ):
            self._loop.call_soon_threadsafe(self._stop_event.set)
        if self._thread is not None:
            self._thread.join(timeout=self._timeout_secs + 2.0)
            self._thread = None

    def __enter__(self) -> TestServerSession:
        self._entered = True
        return self.start()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


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


@overload
def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]],
    fn: Callable[[TestServerSession], None],
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> TestServerSession: ...


@overload
def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: None = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> TestServerSession: ...


def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: Optional[Callable[[TestServerSession], None]] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> TestServerSession:
    session = TestServerSession(
        app=app,
        code=code,
        file_path=file_path,
        inputs=inputs,
        timeout_secs=timeout_secs,
    )
    if fn is not None:
        with session:
            fn(session)
    return session


@overload
def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]],
    fn: Callable[[AsyncTestServerSession], Awaitable[None] | None],
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> Coroutine[Any, Any, AsyncTestServerSession]: ...


@overload
def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: None = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> AsyncTestServerSession: ...


def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: Optional[Callable[[AsyncTestServerSession], Any]] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> Union[AsyncTestServerSession, Coroutine[Any, Any, AsyncTestServerSession]]:
    session = AsyncTestServerSession(
        app=app,
        code=code,
        file_path=file_path,
        inputs=inputs,
        timeout_secs=timeout_secs,
    )
    if fn is not None:

        async def _run_with_callback() -> AsyncTestServerSession:
            async with session:
                res = fn(session)
                if inspect.isawaitable(res):
                    await res
                return session

        return _run_with_callback()
    return session


test_server.__test__ = False  # pyright: ignore[reportFunctionMemberAccess]
test_server_async.__test__ = False  # pyright: ignore[reportFunctionMemberAccess]
