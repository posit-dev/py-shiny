from __future__ import annotations

import asyncio
import dataclasses
import json
import os
import sys
import time
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    get_args,
)

from .._app import App
from .._connection import MockConnection
from .._docstring import no_example
from .._namespaces import ResolvedId, Root
from ..express import is_express_app
from ..express._run import wrap_express_app
from ..session._session import AppSession
from ..types import MISSING
from ..ui import page_fluid

T = TypeVar("T")


VALUE_FIELDS = ("is_ok", "error", "traceback", "inputs", "outputs", "exports")
"""The fields of `TestServerValues`, and the keys of `dict(session)`."""

DEFAULT_CLIENT_DATA: Dict[str, Any] = {
    "output_hidden": False,
    "output_width": 960,
    "output_height": 600,
    "pixelratio": 1,
    "url_protocol": "http:",
    "url_hostname": "localhost",
    "url_port": 0,
    "url_pathname": "/",
    "url_search": "",
    "url_hash": "",
    "url_hash_initial": "",
}
"""
Stand-ins for what a browser would report, sent when the session starts.

Keys are named after the readers on :class:`~shiny.session.ClientData`. An
`output_*` key applies to every output, so `output_width` becomes each output's
`.clientdata_output_<id>_width`; every other key is session-wide. Without these
a size-aware renderer such as `render.plot` raises a silent exception and
produces nothing, and `session.clientdata.url_pathname()` never resolves.
"""


_TIMEOUT_HINT = (
    " Raise `timeout_secs=` if the app is simply slow to start -- a cold"
    " matplotlib font cache, say. A flush that never finishes no matter how"
    " long you wait is usually a reactive cycle: two effects that each write a"
    " value the other reads keep re-queueing each other forever."
)
"""Appended to every timeout message; the knob is not obvious from the error."""

ValueKind = Literal["input", "output", "export"]
ValueStatus = Literal["ok", "error", "silent", "never-rendered"]


@dataclass(frozen=True, eq=False)
class TestServerValue:
    """
    One input, output, or exported value, and how it turned out.

    Returned by `TestServerSession.get_input`, `get_output`, and `get_export`, and
    held by `TestServerValues`.

    Compares equal to the underlying `value`, so the common assertion needs no
    unwrapping:

    ```python
    assert ts.get_output("name") == "foo"   # same as `.value == "foo"`
    ```

    Unless `status` is `"ok"` there is no value to compare against, and the
    comparison raises `ValueError` saying why. Returning `False` would let
    `!= "hi"` pass for an output that never rendered or that raised, hiding the
    real problem behind an assertion that appears to succeed.

    Comparing against another `TestServerValue` compares every field instead,
    and never raises. Because equality is against arbitrary values, instances
    are not hashable.

    Attributes
    ----------
    name
        The input id, output id, or export name.
    kind
        Which of the three this is.
    status
        * `"ok"` — produced a value, available as `value`.
        * `"error"` — raised; see `error` and `traceback`.
        * `"silent"` — the most recent render produced nothing, because a
          `req()` failed (any `SilentException`). The browser blanks such an
          output, so it has no `value` here either, even if an earlier render
          produced one. An output reading an input that has not been set is
          silent, and so is a `render.plot` until the client's width and height
          are supplied.
        * `"never-rendered"` — has not run at all yet, so it has produced
          neither a value, nor an error, nor a silent render. An output that is
          hidden (and so suspended) is never-rendered until it becomes visible.

        There is no status for "does not exist": a `TestServerValue` always
        describes something real, and asking for a name that is not there raises
        `KeyError` instead.
    value
        The value, JSON round-tripped as it would be sent to the browser, so its
        shape depends on the renderer. :data:`~shiny.types.MISSING` unless
        `status` is `"ok"` -- not `None`, which a renderer can legitimately
        produce. (`MISSING` is not JSON-serializable, so
        `json.dumps(dataclasses.asdict(values))` needs `default=str`; `dict()`
        omits the key instead.)
    error
        The error message, or `None` unless `status` is `"error"`.
    traceback
        The formatted traceback of `error`, or `None` when there is no `error`.
        Recorded only in test mode, and never sent to the browser.

    See Also
    --------
    * :class:`~shiny.testserver.TestServerValues`
    * :func:`~shiny.testserver.test_server`
    """

    __test__ = False

    name: str
    kind: ValueKind
    status: ValueStatus
    value: Any = MISSING
    error: Optional[str] = None
    traceback: Optional[str] = None

    def __post_init__(self) -> None:
        # Frozen, so an instance that starts out incoherent stays that way. The
        # states below cannot arise from a real session, and silently tolerating
        # them would mean `error` and `status` could disagree about what happened.
        if self.status not in get_args(ValueStatus):
            raise ValueError(
                f"`status` must be one of {get_args(ValueStatus)}; got"
                f" {self.status!r}."
            )
        if self.status == "error" and self.error is None:
            raise ValueError(
                "A `TestServerValue` with status 'error' needs an `error`."
            )
        if self.status != "error" and self.error is not None:
            raise ValueError(
                f"Only a `TestServerValue` with status 'error' may carry an"
                f" `error`; got status {self.status!r}."
            )
        if self.error is None and self.traceback is not None:
            raise ValueError(
                "A `TestServerValue` with no `error` cannot carry a `traceback`."
            )
        if self.status == "ok" and self.value is MISSING:
            raise ValueError(
                "A `TestServerValue` with status 'ok' needs a `value`; pass"
                " `None` if that is what the renderer produced."
            )
        if self.status != "ok" and self.value is not MISSING:
            raise ValueError(
                f"Only a `TestServerValue` with status 'ok' may carry a `value`;"
                f" got status {self.status!r}."
            )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TestServerValue):
            return dataclasses.astuple(self) == dataclasses.astuple(other)
        # Comparing against a raw value is a convenience this class adds, so it
        # answers the question the test is really asking. Unless the item
        # produced a value there is nothing to answer with, and returning `False`
        # would let `!=` pass while hiding why.
        if self.status == "silent":
            raise ValueError(
                f"{self.kind.capitalize()} {self.name!r} rendered nothing, so"
                " there is no value to compare against: a `req()` failed, which"
                " blanks the output. A dependency was unavailable: an input that"
                " was never set, or a size the client never reported. Set what it"
                " needs first, or check `.status`."
            )
        if self.status == "never-rendered":
            raise ValueError(
                f"{self.kind.capitalize()} {self.name!r} never rendered, so there"
                " is no value to compare against. It has not run at all -- a"
                " hidden output stays suspended until it becomes visible. Check"
                " `.status`."
            )
        if self.status == "error":
            raise ValueError(
                f"{self.kind.capitalize()} {self.name!r} raised, so there is no"
                f" value to compare against: {self.error}. Compare `.error`, or"
                " read `.traceback` for where it came from."
            )
        return self.value == other

    def keys(self) -> Tuple[str, ...]:
        """
        Return the keys `dict(value)` produces.

        Keyed on `status`, not on inspecting `value`: an item that produced no
        value has no `value` key at all, rather than one holding `MISSING`. That
        also keeps the dictionary form JSON-serializable.
        """
        if self.status == "ok":
            return ("name", "kind", "status", "value")
        if self.status == "error":
            return ("name", "kind", "status", "error", "traceback")
        return ("name", "kind", "status")

    def __getitem__(self, key: str) -> Any:
        """Return one field, so that `dict(value)` works."""
        if key not in self.keys():
            raise KeyError(key)
        return getattr(self, key)

    def __repr__(self) -> str:
        # Keeps pytest's assertion output readable when a comparison fails. Only
        # the field that `status` makes meaningful is shown: there is no value
        # unless the item rendered, and no error unless it raised.
        if self.status == "ok":
            extra = f", value={self.value!r}"
        elif self.status == "error":
            extra = f", error={self.error!r}"
        else:
            extra = ""
        return (
            f"{type(self).__name__}({self.name!r}, kind={self.kind!r},"
            f" status={self.status!r}{extra})"
        )


@dataclass(frozen=True)
class TestServerValues:
    """
    A point-in-time snapshot of a test session's input, output, and export values.

    Returned by `TestServerSession.to_values` and
    `AsyncTestServerSession.to_values`. The values are copies, so a snapshot stays
    valid after the session it came from is closed.

    `dict(values)` converts it to plain data, all the way down: each
    `TestServerValue` becomes a dictionary carrying only the keys its `status`
    makes meaningful, so the result is JSON-serializable. `dict(session)` is the
    same thing without capturing a snapshot first.

    `dataclasses.asdict()` also works, but keeps every field of every value --
    including `MISSING`, which JSON cannot encode.

    Attributes
    ----------
    is_ok
        `True` when no output or export errored and no fatal error occurred.
    error
        A summary of the first fatal error, or a count of item errors, or `None`
        when `is_ok` is `True`.
    traceback
        The formatted traceback of the first *fatal* error, or `None` when there
        is no `error`. Per-item tracebacks live on each `TestServerValue`.
    inputs
        Every input the session has received, keyed by input id.
    outputs
        Every registered output, keyed by output id, including ones that errored
        or never rendered.
    exports
        Values registered with `shiny.testmode.export_test_values`, keyed by name.

    See Also
    --------
    * :class:`~shiny.testserver.TestServerValue`
    * :func:`~shiny.testserver.test_server`
    """

    __test__ = False

    is_ok: bool
    error: Optional[str]
    traceback: Optional[str]
    inputs: Dict[str, TestServerValue]
    outputs: Dict[str, TestServerValue]
    exports: Dict[str, TestServerValue]

    def keys(self) -> Tuple[str, ...]:
        """Return the keys `dict(values)` produces."""
        return VALUE_FIELDS

    def __getitem__(self, key: str) -> Any:
        """
        Return one field, so that `dict(values)` works.

        The three value blocks are converted all the way down, so the result is
        plain data. Read the attributes instead to keep the rich
        `TestServerValue`s.
        """
        if key not in VALUE_FIELDS:
            raise KeyError(key)
        field = getattr(self, key)
        if key in ("inputs", "outputs", "exports"):
            return {name: dict(item) for name, item in field.items()}
        return field


def _failures(
    outputs: Dict[str, TestServerValue], exports: Dict[str, TestServerValue]
) -> Dict[str, TestServerValue]:
    """Every output and export that errored, keyed by name."""
    return {
        name: item
        for name, item in (*outputs.items(), *exports.items())
        if item.status == "error"
    }


def _error_summary(
    outputs: Dict[str, TestServerValue],
    exports: Dict[str, TestServerValue],
    fatal_errors: List[Tuple[Exception, str]],
) -> Optional[str]:
    """A summary of the first error, or `None` when nothing errored."""
    if fatal_errors:
        first_exc, _ = fatal_errors[0]
        return f"Session fatal error: {type(first_exc).__name__}: {first_exc}"
    failures = _failures(outputs, exports)
    if failures:
        return f"{len(failures)} error(s): {', '.join(sorted(failures))}"
    return None


def _snapshot_error(value: Any) -> Optional[str]:
    """
    Return the error a test-snapshot value carries, or `None` if it is a value.

    `_build_test_snapshot()` reports failures as single-key marker dictionaries
    rather than raising, so that one bad item never fails the whole snapshot.
    """
    if not isinstance(value, dict):
        return None
    for marker in (
        "__shiny_output_error__",
        "__shiny_snapshot_preprocess_error__",
        "__shiny_serialization_error__",
    ):
        if marker in value:
            return str(cast(Dict[str, Any], value)[marker])
    return None


def _require_item(
    items: Dict[str, TestServerValue], name: str, kind: ValueKind
) -> TestServerValue:
    """
    Return `name`'s value, or raise naming what is actually there.

    A name that does not exist is a mistake in the test, not a state a value can
    be in, so it fails at the lookup rather than returning something that
    compares unequal to everything later on.
    """
    if name in items:
        return items[name]
    known = ", ".join(repr(key) for key in sorted(items)) or "none"
    raise KeyError(f"No {kind} named {name!r}. Available: {known}.")


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

    `async with` is the only supported way to run a session: it starts the app on
    entry and always tears it down on exit, including when the test fails. Values
    registered with `shiny.testmode.export_test_values` are read with
    `get_export`.

    See Also
    --------
    * :func:`~shiny.testserver.test_server_async`
    * :class:`~shiny.testserver.TestServerSession`
    * :class:`~shiny.testserver.TestServerValues`
    """

    __test__ = False

    def __init__(
        self,
        app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
        *,
        client_data: Optional[Mapping[str, Any]] = None,
        timeout_secs: float = 5.0,
    ) -> None:
        self._target_app = app
        self._client_data = dict(client_data or {})
        self._timeout_secs = timeout_secs

        self.ns: ResolvedId = Root
        """The namespace these ids are read in; `Root` (`""`) for a session."""

        self._app_obj: Optional[App] = None
        self._session: Optional[AppSession] = None
        self._conn: Optional[MockConnection] = None
        self._session_task: Optional[asyncio.Task[None]] = None
        self._saved_sys_path: Optional[List[str]] = None
        self._saved_modules: Optional[Set[str]] = None
        self._app_dir: Optional[Path] = None
        self._old_testmode: Optional[str] = None
        self._old_app_test_mode: Optional[bool] = None
        self._old_app_server: Optional[Callable[..., Any]] = None
        self._fatal_errors: List[Tuple[Exception, str]] = []
        self._current_inputs: Dict[str, TestServerValue] = {}
        self._current_outputs: Dict[str, TestServerValue] = {}
        self._current_exports: Dict[str, TestServerValue] = {}
        self._is_started: bool = False

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
            # Only forget modules loaded from the app's own directory, so a
            # sibling `helpers.py` in another app can load fresh next time.
            # Anything else imported meanwhile (matplotlib, pandas, shiny's own
            # lazy submodules) must stay: re-executing those breaks C extensions
            # and duplicates registries.
            if self._app_dir is not None:
                for mod_name in set(sys.modules) - self._saved_modules:
                    origin = getattr(sys.modules.get(mod_name), "__file__", None)
                    if origin and Path(origin).resolve().is_relative_to(self._app_dir):
                        sys.modules.pop(mod_name, None)
            self._saved_modules = None
            self._app_dir = None

        if self._old_testmode is not None:
            os.environ["SHINY_TESTMODE"] = self._old_testmode
            self._old_testmode = None
        else:
            os.environ.pop("SHINY_TESTMODE", None)

        if self._app_obj is not None:
            if self._old_app_test_mode is not None:
                self._app_obj._test_mode = self._old_app_test_mode
                self._old_app_test_mode = None
            if self._old_app_server is not None:
                self._app_obj.server = self._old_app_server
                self._old_app_server = None

    async def _start(self) -> AsyncTestServerSession:
        try:
            return await self._start_impl()
        except Exception:
            await self._cleanup()
            raise

    def _load_app_path(self, target_path: Path) -> Optional[App]:
        """Import an app file (Core or Express), with its directory on `sys.path`."""
        target_path = target_path.resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {target_path}")
        self._app_dir = target_path.parent
        sys.path.insert(0, str(target_path.parent))
        if is_express_app(str(target_path), app_dir=None):
            return wrap_express_app(target_path)
        return _load_app_from_file(target_path)

    async def _start_impl(self) -> AsyncTestServerSession:
        self._old_testmode = os.environ.get("SHINY_TESTMODE")
        os.environ["SHINY_TESTMODE"] = "1"
        self._saved_sys_path = list(sys.path)
        self._saved_modules = set(sys.modules.keys())

        if self._target_app is None:
            raise ValueError("`app` must be provided.")
        if isinstance(self._target_app, App):
            self._app_obj = self._target_app
        elif callable(self._target_app):
            self._app_obj = App(page_fluid(), self._target_app)
        elif isinstance(self._target_app, (str, Path)):
            self._app_obj = self._load_app_path(Path(self._target_app))
        else:
            raise TypeError(
                "`app` must be a server function, a `shiny.App`, or a path to"
                f" an app file; got {type(self._target_app).__name__}."
            )

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

            client_data = {**DEFAULT_CLIENT_DATA, **self._client_data}
            per_output = {
                key[len("output_") :]: value
                for key, value in client_data.items()
                if key.startswith("output_")
            }
            unhide_data: Dict[str, Any] = {
                f".clientdata_{key}": value
                for key, value in client_data.items()
                if not key.startswith("output_")
            }
            for out_name in self._session.output._outputs.keys():
                for suffix, value in per_output.items():
                    unhide_data[f".clientdata_output_{out_name}_{suffix}"] = value

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
                f"test_server timed out after {self._timeout_secs}s during session"
                f" initialization.{_TIMEOUT_HINT}"
            )
        try:
            await asyncio.wait_for(initial_flush_done.wait(), timeout=remaining)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s waiting for"
                f" initial flush.{_TIMEOUT_HINT}"
            )

        if not self._fatal_errors and not self._session_task.done():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"test_server timed out after {self._timeout_secs}s during session"
                    f" initialization.{_TIMEOUT_HINT}"
                )
            try:
                await asyncio.wait_for(unhide_flush_done.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"test_server timed out after {self._timeout_secs}s waiting for"
                    f" output initialization.{_TIMEOUT_HINT}"
                )

        # A server function that blocks without awaiting holds the event loop, so
        # the waits above cannot fire while it runs and may instead return late.
        # Checking the clock reports the overrun either way. See `set_inputs`.
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s during session"
                f" initialization.{_TIMEOUT_HINT}"
            )

        await asyncio.sleep(0.01)
        await self._refresh_snapshots()
        return self

    async def _refresh_snapshots(self) -> None:
        if self._session is None:
            return
        snapshot = await self._session._build_test_snapshot()
        queues = self._session._outbound_message_queues

        self._current_inputs = {
            name: TestServerValue(name, "input", "ok", value)
            for name, value in snapshot.get("input", {}).items()
        }

        # The snapshot keeps each output's last computed value even when the
        # latest render was silenced (Shiny for R parity), so `test_silent` --
        # which only holds outputs whose latest render produced nothing -- is
        # what distinguishes "blank now" from "never ran".
        raw_outputs: Dict[str, Any] = snapshot.get("output", {})
        self._current_outputs = {}
        for name in self._session.output._outputs.keys():
            error = _snapshot_error(raw_outputs.get(name))
            if name in queues.test_silent:
                self._current_outputs[name] = TestServerValue(name, "output", "silent")
            elif error is not None:
                self._current_outputs[name] = TestServerValue(
                    name,
                    "output",
                    "error",
                    error=error,
                    traceback=queues.test_tracebacks.get(name),
                )
            elif name in raw_outputs:
                self._current_outputs[name] = TestServerValue(
                    name, "output", "ok", raw_outputs[name]
                )
            else:
                self._current_outputs[name] = TestServerValue(
                    name, "output", "never-rendered"
                )

        self._current_exports = {}
        for name, value in snapshot.get("export", {}).items():
            error = _snapshot_error(value)
            self._current_exports[name] = (
                TestServerValue(name, "export", "error", error=error)
                if error is not None
                else TestServerValue(name, "export", "ok", value)
            )

    async def set_inputs(self, /, **kwargs: Any) -> AsyncTestServerSession:
        """
        Set input values and wait for the resulting reactive flush.

        Simulates a user interaction: the values are sent to the session as an
        input update, and the call returns once the reactive graph has settled
        and the values read by `get_input`, `get_output`, and `get_export` have
        been refreshed.

        Parameters
        ----------
        **kwargs
            Input values keyed by input id. Ids that are not valid Python
            identifiers -- a module's namespaced `"counter-n"`, say -- go
            through an unpacked dictionary: `set_inputs(**{"counter-n": 7})`.

        Returns
        -------
        :
            This session, so calls can be chained.

        Raises
        ------
        TimeoutError
            If the flush does not complete within `timeout_secs`.
        RuntimeError
            If the session is not running, or has already ended because of a
            fatal error.
        """
        all_inputs: Dict[str, Any] = dict(kwargs)

        if self._conn is None or self._session is None:
            raise RuntimeError("Session is not running.")
        if self._session_task is not None and self._session_task.done():
            # Nothing reads the connection any more, so waiting on a flush
            # would only time out and hide the error that ended the session.
            raise RuntimeError(f"The session has ended. {self.error}")

        flush_done = asyncio.Event()
        unreg: Optional[Callable[[], None]] = None

        def on_set_inputs_flushed() -> None:
            flush_done.set()

        unreg = self._session.on_flushed(on_set_inputs_flushed, once=False)
        self._conn.cause_receive(json.dumps({"method": "update", "data": all_inputs}))
        started = time.monotonic()
        timed_out = False
        try:
            await asyncio.wait_for(flush_done.wait(), timeout=self._timeout_secs)
        except asyncio.TimeoutError:
            timed_out = True
        finally:
            if unreg is not None:
                try:
                    unreg()
                except Exception:
                    pass

        # Reactive code that blocks without awaiting holds the event loop, so
        # `wait_for` cannot fire while it runs and the flush may instead finish
        # late. Checking the clock as well reports the overrun either way, rather
        # than leaving it to a race between the timeout and the flush.
        if timed_out or time.monotonic() - started > self._timeout_secs:
            raise TimeoutError(
                f"test_server timed out after {self._timeout_secs}s waiting for the"
                f" reactive flush following set_inputs().{_TIMEOUT_HINT}"
            )

        await asyncio.sleep(0.01)
        await self._refresh_snapshots()
        return self

    async def flush(self) -> AsyncTestServerSession:
        """
        Re-read the session's output, export, and error values.

        `set_inputs` already does this, so an explicit call is only needed after
        something outside the test changes reactive state (for example an effect
        driven by a timer).

        Returns
        -------
        :
            This session, so calls can be chained.
        """
        await self._refresh_snapshots()
        return self

    @property
    def is_ok(self) -> bool:
        """`True` when nothing errored and no fatal error occurred."""
        return (
            not _failures(self._current_outputs, self._current_exports)
            and not self._fatal_errors
        )

    @property
    def error(self) -> Optional[str]:
        """A summary of the first error, or `None` when `is_ok` is `True`."""
        return _error_summary(
            self._current_outputs, self._current_exports, self._fatal_errors
        )

    def make_scope(self, id: str) -> AsyncTestServerScope:
        """
        Return a view of this session namespaced to a module instance.

        Mirrors `shiny.Session.make_scope`: inside a module the app's server code
        uses bare ids, and so does the returned view, while the session underneath
        keeps the namespaced ones.

        Parameters
        ----------
        id
            The id the module instance was given, as in `counter_server("counter")`.

        Returns
        -------
        :
            An `AsyncTestServerScope` reading and writing the same live session.

        See Also
        --------
        * :class:`~shiny.testserver.AsyncTestServerScope`
        """
        return AsyncTestServerScope(self, self.ns(id))

    def root_scope(self) -> AsyncTestServerSession:
        """
        Return this session, which is already the root.

        Mirrors `shiny.Session.root_scope`, so code handed either a session or an
        `AsyncTestServerScope` can reach the session without a type check.
        """
        return self

    def get_input(self, name: str) -> TestServerValue:
        """
        Return one input value.

        Parameters
        ----------
        name
            An input id.

        Returns
        -------
        :
            A `TestServerValue`. It compares equal to the value itself, so
            `session.get_input("n") == 10` works.

        Raises
        ------
        KeyError
            If the session has not received that input.
        """
        return _require_item(self._current_inputs, name, "input")

    def get_output(self, name: str) -> TestServerValue:
        """
        Return one output value.

        Parameters
        ----------
        name
            An output id.

        Returns
        -------
        :
            A `TestServerValue`, with `status` `"silent"` if the output's latest
            render produced nothing. It compares equal to the value itself, so
            `session.get_output("txt") == "hi"` works.

        Raises
        ------
        KeyError
            If the app has no such output.
        """
        return _require_item(self._current_outputs, name, "output")

    def get_export(self, name: str) -> TestServerValue:
        """
        Return one exported test value.

        Parameters
        ----------
        name
            A name passed to `shiny.testmode.export_test_values`.

        Returns
        -------
        :
            A `TestServerValue`. It compares equal to the value itself, so
            `session.get_export("doubled") == 40` works.

        Raises
        ------
        KeyError
            If that name was not exported.
        """
        return _require_item(self._current_exports, name, "export")

    def to_values(self) -> TestServerValues:
        """
        Capture the session's current state.

        Returns
        -------
        :
            A `TestServerValues` snapshot of copies, which stays valid after the
            session is closed.
        """
        return TestServerValues(
            is_ok=self.is_ok,
            error=self.error,
            traceback=self._fatal_errors[0][1] if self._fatal_errors else None,
            inputs=dict(self._current_inputs),
            outputs=dict(self._current_outputs),
            exports=dict(self._current_exports),
        )

    def keys(self) -> Tuple[str, ...]:
        """Return the keys `dict(session)` produces. See `TestServerValues`."""
        return VALUE_FIELDS

    def __getitem__(self, key: str) -> Any:
        """
        Return one `TestServerValues` field, so that `dict(session)` works.

        Equivalent to `dict(session.to_values())`: plain data all the way down.
        Use `to_values()` to keep the rich `TestServerValue`s.
        """
        return self.to_values()[key]

    async def _close(self) -> None:
        self._is_started = False
        await self._cleanup()

    async def __aenter__(self) -> AsyncTestServerSession:
        """
        Load the app, start the session, and wait for the initial reactive flush.

        Returns
        -------
        :
            The started session.

        Raises
        ------
        TimeoutError
            If the session does not finish its initial flush within
            `timeout_secs`.
        FileNotFoundError
            If the app was given as a path that does not exist.
        ValueError
            If `app` was not provided.
        RuntimeError
            If the target does not yield a `shiny.App` instance.
        """
        return await self._start()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Disconnect the session and undo everything entering it set up.

        Restores `sys.path`, `sys.modules`, the `SHINY_TESTMODE` environment
        variable, and the app object's test-mode state. Runs even when the body
        raised.
        """
        await self._close()


class TestServerSession:
    """
    An in-memory Shiny session driven from ordinary (non-async) test code.

    Construct one with `test_server` rather than directly. The session runs the
    app's server function against a mock connection — no browser and no network
    server — so inputs can be set and outputs asserted in process.

    `with` is the only supported way to run a session: it starts the app on entry
    and always tears it down on exit, including when the test fails. Set inputs to
    simulate user interactions, and read outputs between them:

    ```python
    with test_server(app_path) as ts:
        ts.set_inputs(a=1, b=2)
        assert ts.get_output("name") == "foo"
        ts.set_inputs(a=3, b=4)
        assert ts.get_output("name") == "bar"
    ```

    Values registered with `shiny.testmode.export_test_values` are read with
    `get_export`. To keep values for assertions after the block, capture a
    `TestServerValues` with `to_values`, or a plain dictionary with
    `dict(session)`, while the session is still open.

    This class drives its own event loop on the calling thread, so it cannot be
    used from inside a running event loop — in an `async` test, use
    `test_server_async` instead.

    See Also
    --------
    * :func:`~shiny.testserver.test_server`
    * :class:`~shiny.testserver.AsyncTestServerSession`
    * :class:`~shiny.testserver.TestServerValues`
    """

    __test__ = False

    def __init__(
        self,
        app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
        *,
        client_data: Optional[Mapping[str, Any]] = None,
        timeout_secs: float = 5.0,
    ) -> None:
        self._async_session = AsyncTestServerSession(
            app=app,
            client_data=client_data,
            timeout_secs=timeout_secs,
        )
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._timeout_secs = timeout_secs
        self._is_running = False

        self.ns: ResolvedId = Root
        """The namespace these ids are read in; `Root` (`""`) for a session."""

    def _run(self, coro: Coroutine[Any, Any, T]) -> T:
        if self._loop is None:
            coro.close()
            raise RuntimeError("Event loop not initialized.")
        return self._loop.run_until_complete(coro)

    def _require_running(self) -> AsyncTestServerSession:
        if not self._is_running:
            raise RuntimeError(
                "The test session is not running. Use it as a context manager:"
                "\n\n    with test_server(...) as ts:\n        ..."
            )
        return self._async_session

    def set_inputs(self, /, **kwargs: Any) -> TestServerSession:
        """
        Set input values and wait for the resulting reactive flush.

        Simulates a user interaction: the values are sent to the session as an
        input update, and the call returns once the reactive graph has settled
        and the values read by `get_input`, `get_output`, and `get_export` have
        been refreshed.

        Parameters
        ----------
        **kwargs
            Input values keyed by input id. Ids that are not valid Python
            identifiers -- a module's namespaced `"counter-n"`, say -- go
            through an unpacked dictionary: `set_inputs(**{"counter-n": 7})`.

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
        self._run(self._require_running().set_inputs(**kwargs))
        return self

    def flush(self) -> TestServerSession:
        """
        Re-read the session's output, export, and error values.

        `set_inputs` already does this, so an explicit call is only needed after
        something outside the test changes reactive state (for example an effect
        driven by a timer).

        Returns
        -------
        :
            This session, so calls can be chained.

        Raises
        ------
        RuntimeError
            If the session is not running.
        """
        self._run(self._require_running().flush())
        return self

    @property
    def is_ok(self) -> bool:
        """`True` when no reactive errors and no fatal errors have occurred."""
        return self._require_running().is_ok

    @property
    def error(self) -> Optional[str]:
        """A summary of the first error, or `None` when `is_ok` is `True`."""
        return self._require_running().error

    def make_scope(self, id: str) -> TestServerScope:
        """
        Return a view of this session namespaced to a module instance.

        Mirrors `shiny.Session.make_scope`: inside a module the app's server code
        uses bare ids, and so does the returned view, while the session underneath
        keeps the namespaced ones.

        Parameters
        ----------
        id
            The id the module instance was given, as in `counter_server("counter")`.

        Returns
        -------
        :
            A `TestServerScope` reading and writing the same live session.

        See Also
        --------
        * :class:`~shiny.testserver.TestServerScope`
        """
        return TestServerScope(self, self.ns(id))

    def root_scope(self) -> TestServerSession:
        """
        Return this session, which is already the root.

        Mirrors `shiny.Session.root_scope`, so code handed either a session or a
        `TestServerScope` can reach the session without a type check.
        """
        return self

    def get_input(self, name: str) -> TestServerValue:
        """
        Return one input value.

        Parameters
        ----------
        name
            An input id.

        Returns
        -------
        :
            A `TestServerValue`. It compares equal to the value itself, so
            `session.get_input("n") == 10` works.

        Raises
        ------
        KeyError
            If the session has not received that input.
        """
        return self._require_running().get_input(name)

    def get_output(self, name: str) -> TestServerValue:
        """
        Return one output value.

        Parameters
        ----------
        name
            An output id.

        Returns
        -------
        :
            A `TestServerValue`, with `status` `"silent"` if the output's latest
            render produced nothing. It compares equal to the value itself, so
            `session.get_output("txt") == "hi"` works.

        Raises
        ------
        KeyError
            If the app has no such output.
        """
        return self._require_running().get_output(name)

    def get_export(self, name: str) -> TestServerValue:
        """
        Return one exported test value.

        Parameters
        ----------
        name
            A name passed to `shiny.testmode.export_test_values`.

        Returns
        -------
        :
            A `TestServerValue`. It compares equal to the value itself, so
            `session.get_export("doubled") == 40` works.

        Raises
        ------
        KeyError
            If that name was not exported.
        """
        return self._require_running().get_export(name)

    def to_values(self) -> TestServerValues:
        """
        Capture the session's current state.

        Returns
        -------
        :
            A `TestServerValues` snapshot of copies, so it stays valid after the
            `with` block ends.
        """
        return self._require_running().to_values()

    def keys(self) -> Tuple[str, ...]:
        """Return the keys `dict(session)` produces. See `TestServerValues`."""
        return VALUE_FIELDS

    def __getitem__(self, key: str) -> Any:
        """
        Return one `TestServerValues` field, so that `dict(session)` works.

        Equivalent to `dict(session.to_values())`: plain data all the way down.
        Use `to_values()` to keep the rich `TestServerValue`s.
        """
        return self.to_values()[key]

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

    def __enter__(self) -> TestServerSession:
        """
        Load the app, start the session, and wait for the initial reactive flush.

        Returns
        -------
        :
            The started session.

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
            If `app` was not provided.
        """
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
            self._run(self._async_session._start())
        except BaseException:
            # `AsyncTestServerSession._start()` cleans up after itself on failure,
            # so only the loop needs tearing down here.
            self._close_loop()
            raise
        self._is_running = True
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Disconnect the session, undo everything entering it set up, close the loop.

        Restores `sys.path`, `sys.modules`, the `SHINY_TESTMODE` environment
        variable, and the app object's test-mode state. Runs even when the body
        raised.
        """
        if not self._is_running:
            return
        self._is_running = False
        try:
            self._run(self._async_session._close())
        finally:
            self._close_loop()


class _TestServerScopeBase:
    """
    The half of a scope that only reads, shared by the sync and async flavors.

    A scope holds no state of its own beyond `ns`: every read goes to the live
    session, so a scope taken early keeps working across later `set_inputs`.
    """

    __test__ = False

    def __init__(self, ns: ResolvedId) -> None:
        self.ns = ns
        """The namespace these ids are read in, such as `"counter"`."""

    @property
    def _session(self) -> AsyncTestServerSession:
        raise NotImplementedError  # pragma: no cover

    def _resolve(self, name: str) -> str:
        """Namespace one id the way the module's own server code would."""
        if name.startswith("."):
            # `.clientdata_*` is session-wide in Shiny -- a `SessionProxy` reads
            # it from the root -- so namespacing it here would quietly produce an
            # id nothing reads.
            raise ValueError(
                f"{name!r} is session-wide, so it cannot be set on the"
                f" {str(self.ns)!r} scope. Set it on the session instead, via"
                " `scope.root_scope()`."
            )
        return str(self.ns(name))

    def _in_scope(
        self, items: Dict[str, TestServerValue]
    ) -> Dict[str, TestServerValue]:
        """Keep only this namespace's items, re-keyed by the bare id."""
        prefix = f"{str(self.ns)}{ResolvedId._sep}"
        scoped: Dict[str, TestServerValue] = {}
        for name, item in items.items():
            if name.startswith(prefix):
                bare = name[len(prefix) :]
                scoped[bare] = dataclasses.replace(item, name=bare)
        return scoped

    @property
    def _scoped_outputs(self) -> Dict[str, TestServerValue]:
        return self._in_scope(self._session._current_outputs)

    @property
    def _scoped_exports(self) -> Dict[str, TestServerValue]:
        return self._in_scope(self._session._current_exports)

    @property
    def is_ok(self) -> bool:
        """
        `True` when nothing in this namespace errored.

        A *fatal* session error counts against every scope: it is not
        attributable to one module, and a scope reporting `True` while the app
        failed to start would be worse than noise.
        """
        return (
            not _failures(self._scoped_outputs, self._scoped_exports)
            and not self._session._fatal_errors
        )

    @property
    def error(self) -> Optional[str]:
        """A summary of the first error in this namespace, or `None`."""
        return _error_summary(
            self._scoped_outputs, self._scoped_exports, self._session._fatal_errors
        )

    def get_input(self, name: str) -> TestServerValue:
        """
        Return one input value, named as the module's own code names it.

        Raises
        ------
        KeyError
            If the session has not received that input in this namespace.
        """
        return _require_item(
            self._in_scope(self._session._current_inputs), name, "input"
        )

    def get_output(self, name: str) -> TestServerValue:
        """
        Return one output value, named as the module's own code names it.

        Raises
        ------
        KeyError
            If this namespace has no such output.
        """
        return _require_item(self._scoped_outputs, name, "output")

    def get_export(self, name: str) -> TestServerValue:
        """
        Return one exported test value, named as the module exported it.

        Raises
        ------
        KeyError
            If this namespace exported no such name.
        """
        return _require_item(self._scoped_exports, name, "export")

    def to_values(self) -> TestServerValues:
        """
        Capture this namespace's current state.

        Returns
        -------
        :
            A `TestServerValues` holding only this namespace's items, keyed by
            bare id -- the same shape a test of the module server on its own
            would produce.
        """
        return TestServerValues(
            is_ok=self.is_ok,
            error=self.error,
            traceback=(
                self._session._fatal_errors[0][1]
                if self._session._fatal_errors
                else None
            ),
            inputs=self._in_scope(self._session._current_inputs),
            outputs=self._scoped_outputs,
            exports=self._scoped_exports,
        )

    def keys(self) -> Tuple[str, ...]:
        """Return the keys `dict(scope)` produces. See `TestServerValues`."""
        return VALUE_FIELDS

    def __getitem__(self, key: str) -> Any:
        """Return one `TestServerValues` field, so that `dict(scope)` works."""
        return self.to_values()[key]

    def __repr__(self) -> str:
        return f"{type(self).__name__}(ns={str(self.ns)!r})"


class AsyncTestServerScope(_TestServerScopeBase):
    """
    A namespaced view of an `AsyncTestServerSession`.

    Construct one with `AsyncTestServerSession.make_scope` rather than directly.
    It is the test-side counterpart of the `shiny.Session` proxy a module's
    server function receives: ids go in and come out bare, and the session
    underneath sees them namespaced.

    ```python
    async with test_server_async("app.py") as ts:
        counter = ts.make_scope("counter")
        await counter.set_inputs(n=7)
        assert counter.get_output("label") == "n=7"

        # The session still sees the namespaced ids.
        assert ts.get_output("counter-label") == "n=7"
    ```

    See Also
    --------
    * :class:`~shiny.testserver.AsyncTestServerSession`
    * :class:`~shiny.testserver.TestServerScope`
    """

    def __init__(self, session: AsyncTestServerSession, ns: ResolvedId) -> None:
        super().__init__(ns)
        self._root = session

    @property
    def _session(self) -> AsyncTestServerSession:
        return self._root

    def root_scope(self) -> AsyncTestServerSession:
        """Return the session this scope is a view of."""
        return self._root

    def make_scope(self, id: str) -> AsyncTestServerScope:
        """Return a view of a module nested inside this one."""
        return AsyncTestServerScope(self._root, self.ns(id))

    async def set_inputs(self, /, **kwargs: Any) -> AsyncTestServerScope:
        """
        Set input values in this namespace and wait for the reactive flush.

        Parameters
        ----------
        **kwargs
            Input values keyed by the bare id the module's own code uses.

        Returns
        -------
        :
            This scope, so calls can be chained.

        Raises
        ------
        ValueError
            If an id is session-wide (`.clientdata_*`), which no namespace owns.
        """
        await self._root.set_inputs(
            **{self._resolve(name): value for name, value in kwargs.items()}
        )
        return self

    async def flush(self) -> AsyncTestServerScope:
        """Re-read the session's values, and return this scope for chaining."""
        await self._root.flush()
        return self


class TestServerScope(_TestServerScopeBase):
    """
    A namespaced view of a `TestServerSession`.

    Construct one with `TestServerSession.make_scope` rather than directly. It is
    the test-side counterpart of the `shiny.Session` proxy a module's server
    function receives: ids go in and come out bare, and the session underneath
    sees them namespaced.

    ```python
    with test_server("app.py") as ts:
        counter = ts.make_scope("counter")
        counter.set_inputs(n=7)
        assert counter.get_output("label") == "n=7"

        # The session still sees the namespaced ids.
        assert ts.get_output("counter-label") == "n=7"
    ```

    See Also
    --------
    * :class:`~shiny.testserver.TestServerSession`
    * :class:`~shiny.testserver.AsyncTestServerScope`
    """

    def __init__(self, session: TestServerSession, ns: ResolvedId) -> None:
        super().__init__(ns)
        self._root = session

    @property
    def _session(self) -> AsyncTestServerSession:
        return self._root._require_running()

    def root_scope(self) -> TestServerSession:
        """Return the session this scope is a view of."""
        return self._root

    def make_scope(self, id: str) -> TestServerScope:
        """Return a view of a module nested inside this one."""
        return TestServerScope(self._root, self.ns(id))

    def set_inputs(self, /, **kwargs: Any) -> TestServerScope:
        """
        Set input values in this namespace and wait for the reactive flush.

        Parameters
        ----------
        **kwargs
            Input values keyed by the bare id the module's own code uses.

        Returns
        -------
        :
            This scope, so calls can be chained.

        Raises
        ------
        ValueError
            If an id is session-wide (`.clientdata_*`), which no namespace owns.
        """
        self._root.set_inputs(
            **{self._resolve(name): value for name, value in kwargs.items()}
        )
        return self

    def flush(self) -> TestServerScope:
        """Re-read the session's values, and return this scope for chaining."""
        self._root.flush()
        return self


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


DEFAULT_APP_FILE = "app.py"
"""The app file `test_server()` loads when called with no target, like `local_app`."""


def _caller_dir() -> Path:
    """
    Return the directory of the file that called into this module.

    Frame 0 is this function and frame 1 is `test_server`/`test_server_async`, so
    frame 2 is the test module. Resolving relative paths against it (rather than
    the working directory, which pytest sets to the rootdir) matches how
    `local_app` and `create_app_fixture` find an app next to the test file.
    """
    frame = sys._getframe(2)
    caller_file = frame.f_globals.get("__file__")
    # No `__file__` in a REPL or `exec()`; the working directory is the best guess.
    return Path(caller_file).parent.resolve() if caller_file else Path.cwd()


def _resolve_target(
    app: Optional[Union[App, Callable[..., Any], str, Path]],
    caller_dir: Path,
) -> Union[App, Callable[..., Any], str, Path]:
    """
    Apply the `app.py` default and make path targets caller-relative.

    A `Path` that already points at a file is used as-is; anything else is taken
    as relative to `caller_dir`. Passing a `str` therefore always means "relative
    to the test file", matching `create_app_fixture`.
    """
    if app is None:
        app = DEFAULT_APP_FILE
    if isinstance(app, Path) and app.is_file():
        return app
    if isinstance(app, (str, Path)):
        return caller_dir / app
    return app


@no_example()
def test_server(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    *,
    client_data: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> TestServerSession:
    """
    Run a Shiny server function, Express app, or `shiny.App` in memory for testing.

    The Python counterpart to R Shiny's `testServer()`. The app's server function
    runs against a mock connection, so there is no browser and no network server:
    set inputs, let the reactive graph settle, and assert on outputs — all in
    process, in an ordinary (non-async) test.

    `app` accepts every way of naming what to test, and defaults to `"app.py"`
    next to the test file, like the `local_app` fixture. The returned session must
    be used as a context manager, which guarantees the app is torn down even when
    an assertion fails.

    In an `async` test, use `test_server_async` instead — this function drives its
    own event loop and cannot run inside a loop that is already running.

    Parameters
    ----------
    app
        What to test, defaulting to `"app.py"`:

        * A server function, which is wrapped in an app with an empty UI.
        * A `shiny.App` instance.
        * A path to an app file, Core or Express. A `str`, or a `Path` that is not
          already a file, is resolved relative to the directory of the file
          calling `test_server()`. Pass a `str` to be sure a path stays relative.
    client_data
        Stand-ins for what a browser would report, merged over
        `DEFAULT_CLIENT_DATA`. Keys are named after the readers on
        :class:`~shiny.session.ClientData`: an `output_*` key applies to every
        output, and every other key is session-wide. See the note below. `None`
        means the same as `{}`: every default is used.
    timeout_secs
        How long to wait for any single reactive flush, including the initial one,
        before raising `TimeoutError`. Reactive code that blocks without awaiting
        holds the event loop and cannot be interrupted, so an overrun caused that
        way is reported once the flush finishes rather than partway through.

    Returns
    -------
    :
        An unstarted `TestServerSession`, to be used with `with`.


    Notes
    -----
    ::: {.callout-note title="Client data"}
    A real browser reports values back to the server: how big each output is, the
    device pixel ratio, and the parts of the URL. Your app reads them through
    `session.clientdata`, and renderers read them too — `render.plot` needs a
    width and height before it can draw anything.

    There is no browser here, so those inputs would never arrive. A plot would
    render nothing and `session.clientdata.url_pathname()` would never resolve,
    both *silently*: the output would simply be `"silent"` and the session would
    still report success.

    The session therefore sends the stand-ins in `DEFAULT_CLIENT_DATA` as soon as
    it starts, so these work out of the box. Override any of them with
    `client_data=`, and change one output's size mid-test with `set_inputs`.
    :::

    Examples
    --------
    Every way of naming what to test:

    ```python
    test_server()                 # app.py beside the test file
    test_server("myapp.py")       # another file beside the test file
    test_server(path_to_app)      # absolute Path, used as-is
    test_server(my_mod_server)    # server function, or a shiny.App
    ```

    The `with` block guarantees the app is torn down even when an assertion
    fails:

    ```python
    from shiny.testserver import test_server


    def test_doubling_app():
        with test_server("myapp.py") as ts:
            ts.set_inputs(n=10)
            assert ts.get_output("doubled") == "20"
    ```

    For the common case -- `app.py` next to the test file -- the built-in
    `local_server` pytest fixture is that block already entered, so a test body
    is nothing but interactions and assertions. It is what the rest of these
    examples use. Set inputs to simulate a user interacting, and read outputs
    between them. `get_output` compares equal to the value itself, so assertions
    need no unwrapping:

    ```python
    def test_doubling_app(local_server):
        # Several inputs at once.
        local_server.set_inputs(name="Ada", n=10)

        assert local_server.is_ok
        assert local_server.get_output("greeting") == "Hello, Ada!"
        assert local_server.get_output("doubled") == "20"

        # Values registered with `export_test_values()` are read the same way.
        assert local_server.get_export("running_total") == 20

        # A later interaction re-renders. Inputs you do not name keep their
        # values, so `name` is still "Ada" here.
        local_server.set_inputs(n=21)
        assert local_server.get_output("doubled") == "42"
    ```

    `local_server` is function-scoped -- each test gets a fresh session, since a
    session holds the inputs set so far -- and it takes another app file through
    an indirect parametrization:

    ```python
    import pytest


    @pytest.mark.parametrize("local_server", ["other_app.py"], indirect=True)
    def test_the_other_app(local_server):
        local_server.set_inputs(n=10)
        assert local_server.get_output("tripled") == "30"
    ```

    `set_inputs` and `flush` both return what they were called on, so a sequence
    of interactions can be written as one chain:

    ```python
    def test_a_sequence_of_interactions(local_server):
        assert (
            local_server.set_inputs(name="Ada").set_inputs(n=10).get_output("doubled")
            == "20"
        )
    ```

    Each value also says how it turned out, which is what to inspect when an
    assertion is not simply about equality:

    ```python
    def test_reports_a_bad_value(local_server):
        local_server.set_inputs(n=-1)

        assert local_server.is_ok is False
        failed = local_server.get_output("doubled")
        assert failed.status == "error"
        assert "must be positive" in failed.error
        assert "raise ValueError" in failed.traceback
    ```

    Client data has defaults, so a plot renders without a browser. Change one
    output's size partway through a test by setting its `.clientdata_*` input,
    or set every output's size up front with `client_data=` -- an argument only
    `test_server()` takes, so that one is written with the `with` block:

    ```python
    def test_plot_at_a_given_size(local_server):
        local_server.set_inputs(**{".clientdata_output_plot_width": 300})
        assert local_server.get_output("plot").status == "ok"


    def test_every_plot_at_a_given_size():
        with test_server("myapp.py", client_data={"output_width": 300}) as ts:
            assert ts.get_output("plot").status == "ok"
    ```

    A Shiny module namespaces its ids, so reach them through the id the module
    was given:

    ```python
    def test_counter_module(local_server):
        local_server.set_inputs(**{"counter-n": 7})
        assert local_server.get_output("counter-label") == "n=7"
    ```

    Or take a scope and use the bare ids the module's own code uses, the way
    `shiny.Session.make_scope` hands a module its namespaced session:

    ```python
    def test_counter_module_in_scope(local_server):
        counter = local_server.make_scope("counter")
        counter.set_inputs(n=7)
        assert counter.get_output("label") == "n=7"

        # Scoped all the way down: only this module's items, keyed bare.
        assert set(counter.to_values().outputs) == {"label"}
    ```

    A scope holds no state of its own, so take as many as the test needs:

    ```python
    def test_two_counters(local_server):
        first = local_server.make_scope("first")
        first.set_inputs(n=1)
        assert first.get_output("label") == "n=1"

        second = local_server.make_scope("second")
        second.set_inputs(n=2)
        assert second.get_output("label") == "n=2"
    ```

    Express modules namespace their ids the same way, so an Express app holding
    `counter("counter")` is reached with the very same ids, and by the same
    scope.

    Nested modules compose their namespaces, so the id is every ancestor id
    joined by `-` -- `local_server.get_output("outer-inner-label")` -- or, as
    scopes, `local_server.make_scope("outer").make_scope("inner").get_output("label")`.

    A module's server function can be tested on its own, with no app file at
    all: `test_server()` wraps it in an app with an empty UI. Here the fixture
    is one you write, since `local_server` only loads files. Keep it
    function-scoped -- the default -- for the same reason `local_server` is:

    ```python
    import pytest

    from shiny import Inputs, Outputs, Session, module, render
    from shiny.testserver import test_server


    @module.server
    def counter_server(input: Inputs, output: Outputs, session: Session):
        @render.text
        def label():
            return f"n={input.n()}"


    def app_server(input: Inputs, output: Outputs, session: Session):
        counter_server("counter")


    @pytest.fixture
    def ts():
        with test_server(app_server) as session:
            yield session


    def test_counter_module(ts):
        ts.set_inputs(**{"counter-n": 7})
        assert ts.get_output("counter-label") == "n=7"
    ```

    To assert after the app is gone, capture the values first. Both forms hold
    copies, so they stay valid once the `with` block has closed:

    ```python
    def test_reports_everything():
        with test_server("myapp.py") as ts:
            ts.set_inputs(n=10)
            values = ts.to_values()  # rich `TestServerValue`s
            as_dict = dict(ts)  # the same, as plain JSON-ready data

        assert values.outputs["doubled"].value == "20"
        assert as_dict["outputs"]["doubled"]["value"] == "20"
    ```

    See Also
    --------
    * :func:`~shiny.testserver.test_server_async`
    * :class:`~shiny.testserver.TestServerSession`
    * :class:`~shiny.testserver.TestServerValues`
    * :func:`~shiny.testmode.export_test_values`
    """
    return TestServerSession(
        _resolve_target(app, _caller_dir()),
        client_data=client_data,
        timeout_secs=timeout_secs,
    )


@no_example()
def test_server_async(
    app: Optional[Union[App, Callable[..., Any], str, Path]] = None,
    *,
    client_data: Optional[Mapping[str, Any]] = None,
    timeout_secs: float = 5.0,
) -> AsyncTestServerSession:
    """
    The `async` counterpart to `test_server`, for use in `async` tests.

    Behaves like `test_server` but yields an `AsyncTestServerSession`, whose
    `set_inputs` must be awaited. Use this whenever the test itself is `async`
    (for example under `@pytest.mark.asyncio`) — the synchronous `test_server`
    drives its own event loop and will raise if one is already running.

    Parameters
    ----------
    app
        What to test, defaulting to `"app.py"`:

        * A server function, which is wrapped in an app with an empty UI.
        * A `shiny.App` instance.
        * A path to an app file, Core or Express. A `str`, or a `Path` that is not
          already a file, is resolved relative to the directory of the file
          calling `test_server_async()`. Pass a `str` to be sure a path stays
          relative.
    client_data
        Stand-ins for what a browser would report, merged over
        `DEFAULT_CLIENT_DATA`. Keys are named after the readers on
        :class:`~shiny.session.ClientData`: an `output_*` key applies to every
        output, and every other key is session-wide. See the note below. `None`
        means the same as `{}`: every default is used.
    timeout_secs
        How long to wait for any single reactive flush, including the initial one,
        before raising `TimeoutError`. Reactive code that blocks without awaiting
        holds the event loop and cannot be interrupted, so an overrun caused that
        way is reported once the flush finishes rather than partway through.

    Returns
    -------
    :
        An unstarted `AsyncTestServerSession`, to be used with `async with`.


    Notes
    -----
    ::: {.callout-note title="Client data"}
    A real browser reports values back to the server: how big each output is, the
    device pixel ratio, and the parts of the URL. Your app reads them through
    `session.clientdata`, and renderers read them too — `render.plot` needs a
    width and height before it can draw anything.

    There is no browser here, so those inputs would never arrive. A plot would
    render nothing and `session.clientdata.url_pathname()` would never resolve,
    both *silently*: the output would simply be `"silent"` and the session would
    still report success.

    The session therefore sends the stand-ins in `DEFAULT_CLIENT_DATA` as soon as
    it starts, so these work out of the box. Override any of them with
    `client_data=`, and change one output's size mid-test with `set_inputs`.
    :::

    Examples
    --------
    Every way of naming what to test:

    ```python
    test_server_async()                 # app.py beside the test file
    test_server_async("myapp.py")       # another file beside the test file
    test_server_async(path_to_app)      # absolute Path, used as-is
    test_server_async(my_mod_server)    # server function, or a shiny.App
    ```

    Set inputs to simulate a user interacting, and read outputs between them.
    Only `set_inputs` is awaited; reading a value is not:

    ```python
    import pytest

    from shiny.testserver import test_server_async


    @pytest.mark.asyncio
    async def test_doubling_app():
        async with test_server_async("myapp.py") as ts:
            # Several inputs at once.
            await ts.set_inputs(name="Ada", n=10)

            assert ts.is_ok
            assert ts.get_output("greeting") == "Hello, Ada!"
            assert ts.get_output("doubled") == "20"

            # Values registered with `export_test_values()` are read the same way.
            assert ts.get_export("running_total") == 20

            # A later interaction re-renders. Inputs you do not name keep their
            # values, so `name` is still "Ada" here.
            await ts.set_inputs(n=21)
            assert ts.get_output("doubled") == "42"
    ```

    Each value also says how it turned out, which is what to inspect when an
    assertion is not simply about equality:

    ```python
    @pytest.mark.asyncio
    async def test_reports_a_bad_value():
        async with test_server_async("myapp.py") as ts:
            await ts.set_inputs(n=-1)

            assert ts.is_ok is False
            failed = ts.get_output("doubled")
            assert failed.status == "error"
            assert "must be positive" in failed.error
            assert "raise ValueError" in failed.traceback
    ```

    Client data has defaults, so a plot renders without a browser. Override them
    when a test cares about the size:

    ```python
    @pytest.mark.asyncio
    async def test_plot_at_a_given_size():
        async with test_server_async(
            "myapp.py", client_data={"output_width": 300}
        ) as ts:
            assert ts.get_output("plot").status == "ok"
    ```

    The remaining patterns are the same as for `test_server` -- testing a module
    through its namespaced ids, wrapping the session in a fixture, and capturing
    values that outlive the block -- except that `set_inputs` is awaited.

    See Also
    --------
    * :func:`~shiny.testserver.test_server`
    * :class:`~shiny.testserver.AsyncTestServerSession`
    * :class:`~shiny.testserver.TestServerValues`
    * :func:`~shiny.testmode.export_test_values`
    """
    return AsyncTestServerSession(
        _resolve_target(app, _caller_dir()),
        client_data=client_data,
        timeout_secs=timeout_secs,
    )


test_server.__test__ = False  # pyright: ignore[reportFunctionMemberAccess]
test_server_async.__test__ = False  # pyright: ignore[reportFunctionMemberAccess]
