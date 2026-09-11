from __future__ import annotations

import asyncio
import inspect
import json
import os
import sys
import tempfile
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
    """
    A point-in-time snapshot of a test session's outputs, exports, and errors.

    Returned by `TestServerSession.to_result` and
    `AsyncTestServerSession.to_result`. The values are copies, so a result stays
    valid after the session it came from is closed.

    Also usable as a read-only mapping keyed by attribute name, so
    `result["outputs"]` and `result.outputs` are equivalent.

    Attributes
    ----------
    success
        `True` when the session produced no reactive errors and no fatal errors.
    error
        A summary of the first fatal error, or a count of reactive errors, or
        `None` when `success` is `True`.
    traceback
        The formatted traceback of the first fatal error; `""` if there was none.
    outputs
        Rendered output values, keyed by output id.
    errors
        Errors keyed by the output id that raised them. Errors from values
        registered with `shiny.testmode.export_test_values` are keyed
        `"export:<name>"`, and a fatal session error is keyed `"__fatal__"`.
    exports
        Values registered with `shiny.testmode.export_test_values`, keyed by name.
    elapsed_ms
        Milliseconds elapsed between session start and this snapshot.

    See Also
    --------
    * :func:`~shiny.pytest.test_server`
    * :func:`~shiny.pytest.test_server_async`
    """

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
        """
        Return the result as a plain dictionary.

        Returns
        -------
        :
            A dictionary with one entry per attribute of this class.
        """
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
    """
    An in-memory Shiny session driven from async test code.

    Construct one with `test_server_async` rather than directly. The session runs
    the app's server function against a mock connection — no browser and no
    network server — so inputs can be set and outputs asserted in process.

    Use it as an async context manager to keep the session alive across several
    user interactions:

    ```python
    async with test_server_async(server) as session:
        await session.set_inputs(x=10)
        assert session.outputs["doubled"] == "20"
    ```

    The session is started by `start` and torn down by `close`; entering and
    exiting the context manager does both for you. Values registered with
    `shiny.testmode.export_test_values` are available under `exports`.

    See Also
    --------
    * :func:`~shiny.pytest.test_server_async`
    * :class:`~shiny.pytest.TestServerSession`
    * :class:`~shiny.pytest.TestServerResult`
    """

    __test__ = False

    def __init__(
        self,
        app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
        *,
        code: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        timeout_secs: float = 5.0,
    ) -> None:
        self._target_app = app
        self._target_code = code
        self._target_path = file_path
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
        """
        Load the app, start the session, and wait for the initial reactive flush.

        Called automatically by `__aenter__`. On failure the partially started
        session is cleaned up before the error propagates.

        Returns
        -------
        :
            This session, so the call can be chained.

        Raises
        ------
        TimeoutError
            If the session does not finish its initial flush within
            `timeout_secs`.
        FileNotFoundError
            If the app was given as a path that does not exist.
        ValueError
            If none of `app`, `code`, or `file_path` was provided.
        RuntimeError
            If the target does not yield a `shiny.App` instance.
        """
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

        def custom_print_error(message: Union[str, Exception]) -> None:
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

        self._conn.cause_receive(json.dumps({"method": "init", "data": {}}))

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
    ) -> AsyncTestServerSession:
        """
        Set input values and wait for the resulting reactive flush.

        Simulates a user interaction: the values are sent to the session as an
        input update, and the call returns once the reactive graph has settled and
        `outputs`, `exports`, and `errors` have been refreshed.

        Parameters
        ----------
        inputs
            Input values keyed by input id. Useful for ids that are not valid
            Python identifiers.
        **kwargs
            Input values given as keyword arguments. These take precedence over
            same-named keys in `inputs`.

        Returns
        -------
        :
            This session, so calls can be chained.

        Raises
        ------
        TimeoutError
            If the flush does not complete within `timeout_secs`.
        RuntimeError
            If the session is not running.
        """
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
        return self

    async def flush(self) -> None:
        """
        Re-read the session's outputs, exports, and errors.

        `set_inputs` already does this, so an explicit call is only needed after
        something outside the test changes reactive state (for example an effect
        driven by a timer).
        """
        await self._refresh_snapshots()

    @property
    def outputs(self) -> Dict[str, Any]:
        """Rendered output values, keyed by output id."""
        return dict(self._current_outputs)

    @property
    def exports(self) -> Dict[str, Any]:
        """Values registered with `shiny.testmode.export_test_values`, keyed by name."""
        return dict(self._current_exports)

    @property
    def errors(self) -> Dict[str, Any]:
        """Errors keyed by the output id that raised them. See `TestServerResult`."""
        return dict(self._current_errors)

    @property
    def success(self) -> bool:
        """`True` when no reactive errors and no fatal errors have occurred."""
        return len(self._current_errors) == 0 and len(self._fatal_errors) == 0

    @property
    def error(self) -> Optional[str]:
        """A summary of the first error, or `None` when `success` is `True`."""
        if self._fatal_errors:
            first_exc, _ = self._fatal_errors[0]
            return f"Session fatal error: {type(first_exc).__name__}: {first_exc}"
        if len(self._current_errors) > 0:
            return f"{len(self._current_errors)} reactive error(s) occurred"
        return None

    @property
    def elapsed_ms(self) -> float:
        """Milliseconds elapsed since the session started."""
        return (time.perf_counter() - self._start_time) * 1000.0

    def get_output(self, name: str, default: Any = None) -> Any:
        """
        Return one output value.

        Parameters
        ----------
        name
            An output id.
        default
            The value to return when `name` has no output.

        Returns
        -------
        :
            The rendered output value, or `default`.
        """
        return self._current_outputs.get(name, default)

    def get_export(self, name: str, default: Any = None) -> Any:
        """
        Return one exported test value.

        Parameters
        ----------
        name
            A name passed to `shiny.testmode.export_test_values`.
        default
            The value to return when `name` was not exported.

        Returns
        -------
        :
            The exported value, or `default`.
        """
        return self._current_exports.get(name, default)

    def to_result(self) -> TestServerResult:
        """
        Capture the session's current state.

        Returns
        -------
        :
            A `TestServerResult` snapshot that stays valid after the session is
            closed.
        """
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
        """
        Disconnect the session and undo everything `start` set up.

        Restores `sys.path`, `sys.modules`, the `SHINY_TESTMODE` environment
        variable, and the app object's test-mode state, and removes any temporary
        directory created for `code=`. Called automatically by `__aexit__`.
        """
        self._is_started = False
        await self._cleanup()

    async def __aenter__(self) -> AsyncTestServerSession:
        return await self.start()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()


class TestServerSession(Mapping[str, Any]):
    """
    An in-memory Shiny session driven from ordinary (non-async) test code.

    Construct one with `test_server` rather than directly. The session runs the
    app's server function against a mock connection — no browser and no network
    server — so inputs can be set and outputs asserted in process.

    Use it as a context manager to keep the session alive across several user
    interactions:

    ```python
    with test_server(server) as session:
        session.set_inputs(x=10)
        assert session.outputs["doubled"] == "20"
    ```

    Outside a context manager it is single-shot: the first access to `outputs`,
    `success`, or any other result attribute starts the session if needed,
    captures a `TestServerResult`, and closes it again. Since `set_inputs` returns
    the session, that supports a one-line assertion with no teardown to remember:

    ```python
    assert test_server(server).set_inputs(x=10).outputs["doubled"] == "20"
    ```

    For the same reason the session is also a read-only mapping over that result,
    so `session["outputs"]` is equivalent to `session.outputs`.

    This class drives its own event loop on the calling thread, so it cannot be
    used from inside a running event loop — in an `async` test, use
    `test_server_async` instead.

    See Also
    --------
    * :func:`~shiny.pytest.test_server`
    * :class:`~shiny.pytest.AsyncTestServerSession`
    * :class:`~shiny.pytest.TestServerResult`
    """

    __test__ = False

    def __init__(
        self,
        app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
        *,
        code: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        timeout_secs: float = 5.0,
    ) -> None:
        self._async_session = AsyncTestServerSession(
            app=app,
            code=code,
            file_path=file_path,
            timeout_secs=timeout_secs,
        )
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._timeout_secs = timeout_secs
        self._is_running = False
        self._entered = False
        self._cached_result: Optional[TestServerResult] = None

    def _run(self, coro: Coroutine[Any, Any, T]) -> T:
        if self._loop is None:
            coro.close()
            raise RuntimeError("Event loop not initialized.")
        return self._loop.run_until_complete(coro)

    def start(self) -> TestServerSession:
        """
        Load the app, start the session, and wait for the initial reactive flush.

        Called automatically by `__enter__` and, in single-shot mode, by the first
        result attribute access. Starting an already-running session is a no-op.

        Returns
        -------
        :
            This session, so the call can be chained.

        Raises
        ------
        RuntimeError
            If called from inside a running event loop — use `test_server_async`
            there — or if the target does not yield a `shiny.App` instance.
        TimeoutError
            If the session does not finish its initial flush within
            `timeout_secs`.
        FileNotFoundError
            If the app was given as a path that does not exist.
        ValueError
            If none of `app`, `code`, or `file_path` was provided.
        """
        if self._is_running:
            return self
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            raise RuntimeError(
                "test_server() cannot be used from within a running event loop. "
                "Use `async with test_server_async(...)` instead."
            )

        self._loop = asyncio.new_event_loop()
        try:
            self._run(self._async_session.start())
        except BaseException:
            # `AsyncTestServerSession.start()` cleans up after itself on failure, so
            # only the loop needs tearing down here.
            self._close_loop()
            raise
        self._is_running = True
        return self

    def set_inputs(
        self, inputs: Optional[Mapping[str, Any]] = None, **kwargs: Any
    ) -> TestServerSession:
        """
        Set input values and wait for the resulting reactive flush.

        Simulates a user interaction: the values are sent to the session as an
        input update, and the call returns once the reactive graph has settled and
        `outputs`, `exports`, and `errors` have been refreshed. Starts the session
        first if it is not already running.

        Parameters
        ----------
        inputs
            Input values keyed by input id. Useful for ids that are not valid
            Python identifiers.
        **kwargs
            Input values given as keyword arguments. These take precedence over
            same-named keys in `inputs`.

        Returns
        -------
        :
            This session, so calls can be chained.

        Raises
        ------
        TimeoutError
            If the flush does not complete within `timeout_secs`.
        """
        if not self._is_running:
            self.start()
        self._run(self._async_session.set_inputs(inputs=inputs, **kwargs))
        return self

    def flush(self) -> None:
        """
        Re-read the session's outputs, exports, and errors.

        `set_inputs` already does this, so an explicit call is only needed after
        something outside the test changes reactive state (for example an effect
        driven by a timer). Does nothing if the session is not running.
        """
        if self._is_running:
            self._run(self._async_session.flush())

    def _result(self) -> TestServerResult:
        """
        Current session state.

        Inside a `with` block the caller owns the session's lifetime, so this just
        reads it. Outside one the session is single-shot: it is started if needed,
        snapshotted, and closed again, so that a chained
        `test_server(app).set_inputs(...).outputs` does not leave a session running.
        """
        if self._is_running:
            result = self._async_session.to_result()
            if not self._entered:
                self._cached_result = result
                self.close()
            return result

        if self._cached_result is None:
            self.start()
            self._cached_result = self._async_session.to_result()
            self.close()
        return self._cached_result

    @property
    def outputs(self) -> Dict[str, Any]:
        """Rendered output values, keyed by output id."""
        return self._result().outputs

    @property
    def exports(self) -> Dict[str, Any]:
        """Values registered with `shiny.testmode.export_test_values`, keyed by name."""
        return self._result().exports

    @property
    def errors(self) -> Dict[str, Any]:
        """Errors keyed by the output id that raised them. See `TestServerResult`."""
        return self._result().errors

    @property
    def success(self) -> bool:
        """`True` when no reactive errors and no fatal errors have occurred."""
        return self._result().success

    @property
    def error(self) -> Optional[str]:
        """A summary of the first error, or `None` when `success` is `True`."""
        return self._result().error

    @property
    def traceback(self) -> str:
        """The traceback of the first fatal error; `""` if there was none."""
        return self._result().traceback

    @property
    def elapsed_ms(self) -> float:
        """Milliseconds elapsed since the session started."""
        return self._result().elapsed_ms

    def get_output(self, name: str, default: Any = None) -> Any:
        """
        Return one output value.

        Parameters
        ----------
        name
            An output id.
        default
            The value to return when `name` has no output.

        Returns
        -------
        :
            The rendered output value, or `default`.
        """
        return self.outputs.get(name, default)

    def get_export(self, name: str, default: Any = None) -> Any:
        """
        Return one exported test value.

        Parameters
        ----------
        name
            A name passed to `shiny.testmode.export_test_values`.
        default
            The value to return when `name` was not exported.

        Returns
        -------
        :
            The exported value, or `default`.
        """
        return self.exports.get(name, default)

    def to_result(self) -> TestServerResult:
        """
        Capture the session's current state.

        Returns
        -------
        :
            A `TestServerResult` snapshot that stays valid after the session is
            closed.
        """
        return self._result()

    def to_dict(self) -> Dict[str, Any]:
        """
        Capture the session's current state as a plain dictionary.

        Returns
        -------
        :
            `to_result` converted with `TestServerResult.to_dict`.
        """
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

    def _close_loop(self) -> None:
        loop = self._loop
        self._loop = None
        if loop is None:
            return
        pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
        for t in pending:
            t.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()

    def close(self) -> None:
        """
        Disconnect the session, undo everything `start` set up, and close the loop.

        Restores `sys.path`, `sys.modules`, the `SHINY_TESTMODE` environment
        variable, and the app object's test-mode state, and removes any temporary
        directory created for `code=`. Called automatically by `__exit__`. Closing
        a session that is not running is a no-op.
        """
        if not self._is_running:
            return
        self._is_running = False
        try:
            self._run(self._async_session.close())
        finally:
            self._close_loop()

    def __enter__(self) -> TestServerSession:
        self._entered = True
        return self.start()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Snapshot before closing, so reads after the block see the final state
        # rather than silently re-running the app.
        if self._is_running:
            self._cached_result = self._async_session.to_result()
        self._entered = False
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
    timeout_secs: float = 5.0,
) -> TestServerSession: ...


@overload
def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: None = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    timeout_secs: float = 5.0,
) -> TestServerSession: ...


def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: Optional[Callable[[TestServerSession], None]] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    timeout_secs: float = 5.0,
) -> TestServerSession:
    """
    Run a Shiny server function, Express app, or `shiny.App` in memory for testing.

    The Python counterpart to R Shiny's `testServer()`. The app's server function
    runs against a mock connection, so there is no browser and no network server:
    set inputs, let the reactive graph settle, and assert on outputs — all in
    process, in an ordinary (non-async) test.

    Exactly one of `app`, `code`, or `file_path` identifies what to run.

    There are three ways to use the return value:

    ```python
    # 1. As a context manager, for several sequential interactions.
    with test_server(server) as session:
        session.set_inputs(x=10)
        assert session.outputs["doubled"] == "20"
        session.set_inputs(x=25)
        assert session.outputs["doubled"] == "50"


    # 2. With a callback, in the style of R's `testServer()`.
    def check(session):
        session.set_inputs(x=10)
        assert session.outputs["doubled"] == "20"


    test_server(server, check)

    # 3. Chained, for a single assertion. `set_inputs` returns the session, and
    #    reading a result attribute outside a `with` block closes it again.
    assert test_server(server).set_inputs(x=10).outputs["doubled"] == "20"
    ```

    In an `async` test, use `test_server_async` instead — this function drives its
    own event loop and cannot run inside a loop that is already running.

    Parameters
    ----------
    app
        What to test: a server function, a `shiny.App` instance, or a path to an
        app file (Core or Express). A server function is wrapped in an app with an
        empty UI.
    fn
        A callback to run against the started session. When given, the session is
        started, passed to `fn`, and closed before this function returns.
    code
        Shiny Express or Core source code to run, as a string. Written to a
        temporary `app.py` that is removed when the session closes.
    file_path
        A path to an app file to run. Equivalent to passing the path as `app`.
    timeout_secs
        How long to wait for any single reactive flush, including the initial one,
        before raising `TimeoutError`.

    Returns
    -------
    :
        A `TestServerSession`. It has not been started yet unless `fn` was given,
        in which case it has already been started and closed and holds the final
        result.

    See Also
    --------
    * :func:`~shiny.pytest.test_server_async`
    * :class:`~shiny.pytest.TestServerSession`
    * :class:`~shiny.pytest.TestServerResult`
    * :func:`~shiny.testmode.export_test_values`
    """
    session = TestServerSession(
        app=app,
        code=code,
        file_path=file_path,
        timeout_secs=timeout_secs,
    )
    if fn is not None:
        with session:
            fn(session)
    return session


@overload
def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]],
    fn: Callable[[AsyncTestServerSession], Optional[Awaitable[None]]],
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    timeout_secs: float = 5.0,
) -> Coroutine[Any, Any, AsyncTestServerSession]: ...


@overload
def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: None = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    timeout_secs: float = 5.0,
) -> AsyncTestServerSession: ...


def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    fn: Optional[Callable[[AsyncTestServerSession], Any]] = None,
    *,
    code: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
    timeout_secs: float = 5.0,
) -> Union[AsyncTestServerSession, Coroutine[Any, Any, AsyncTestServerSession]]:
    """
    The `async` counterpart to `test_server`, for use in `async` tests.

    Behaves like `test_server` but yields an `AsyncTestServerSession`, whose
    `set_inputs` must be awaited. Use this whenever the test itself is `async`
    (for example under `@pytest.mark.asyncio`) — the synchronous `test_server`
    drives its own event loop and will raise if one is already running.

    Exactly one of `app`, `code`, or `file_path` identifies what to run.

    ```python
    @pytest.mark.asyncio
    async def test_doubled():
        async with test_server_async(server) as session:
            await session.set_inputs(x=10)
            assert session.outputs["doubled"] == "20"
    ```

    Parameters
    ----------
    app
        What to test: a server function, a `shiny.App` instance, or a path to an
        app file (Core or Express). A server function is wrapped in an app with an
        empty UI.
    fn
        A callback to run against the started session; it may be a coroutine
        function. When given, this function returns an awaitable that starts the
        session, runs `fn`, and closes the session.
    code
        Shiny Express or Core source code to run, as a string. Written to a
        temporary `app.py` that is removed when the session closes.
    file_path
        A path to an app file to run. Equivalent to passing the path as `app`.
    timeout_secs
        How long to wait for any single reactive flush, including the initial one,
        before raising `TimeoutError`.

    Returns
    -------
    :
        An unstarted `AsyncTestServerSession`, to be used with `async with`. If
        `fn` was given, a coroutine that runs `fn` against the session and returns
        it.

    See Also
    --------
    * :func:`~shiny.pytest.test_server`
    * :class:`~shiny.pytest.AsyncTestServerSession`
    * :class:`~shiny.pytest.TestServerResult`
    * :func:`~shiny.testmode.export_test_values`
    """
    session = AsyncTestServerSession(
        app=app,
        code=code,
        file_path=file_path,
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
