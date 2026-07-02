"""Test-mode tools (see `SHINY_TESTMODE`)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Awaitable, Callable

# Import from `shiny.session._utils` directly (not the `shiny.session` package
# __init__): `shiny.session._session` imports from this module, so importing the
# package here would be circular.
from .session._utils import require_active_session

__all__ = (
    "export_test_values",
    "snapshot_preprocess_input",
    "snapshot_preprocess_output",
)


def export_test_values(**kwargs: Callable[[], Any]) -> None:
    """
    Register named values to include in the test-mode snapshot.

    Uses the current reactive session. Each value must be a zero-argument callable
    (a plain function/`lambda` or a `reactive.calc`); it is evaluated lazily, in a
    reactive isolate, when a test snapshot is requested. Registered values appear
    under the `export` block of the snapshot served at
    `/session/{id}/dataobj/shinytest`.

    Has no effect unless test mode is enabled (`SHINY_TESTMODE=1`), so calls can
    be left in production code. Re-registering a name overwrites it.

    To register against a session other than the current one, wrap the call in
    that session's context:

    ```python
    from shiny.session import session_context

    with session_context(other_session):
        export_test_values(my_val=lambda: ...)
    ```

    Parameters
    ----------
    **kwargs
        Named zero-argument callables whose return values are exported.

    Raises
    ------
    RuntimeError
        If there is no active session.

    Examples
    --------
    ```python
    from shiny import App, Inputs, Outputs, Session, reactive, ui
    from shiny.testmode import export_test_values

    app_ui = ui.page_fluid(ui.input_slider("n", "n", 0, 100, 20))

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.calc
        def doubled():
            return input.n() * 2

        # Surface an internal reactive value in the test-mode snapshot.
        # No effect unless `SHINY_TESTMODE=1` is set.
        export_test_values(doubled=doubled)

    app = App(app_ui, server)
    ```
    """
    session = require_active_session(None)
    session._export_test_values(**kwargs)


def snapshot_preprocess_input(
    id: str,
    fn: Callable[[Any], Any] | Callable[[Any], Awaitable[Any]],
) -> None:
    """
    Set a function for preprocessing an input value in test-mode snapshots.

    Uses the current reactive session; equivalent to
    `session.input.set_snapshot_preprocess(id, fn)`. See
    :meth:`~shiny.session.Inputs.set_snapshot_preprocess` for details. Inside a
    module, `id` is resolved in the module's namespace.

    Parameters
    ----------
    id
        The ID of the input value.
    fn
        A function (synchronous or asynchronous) that takes the input value and
        returns the value to write to the test snapshot.

    Raises
    ------
    RuntimeError
        If there is no active session.

    See Also
    --------
    * `shiny.testmode.snapshot_preprocess_output`
    """
    session = require_active_session(None)
    session.input.set_snapshot_preprocess(id, fn)


def snapshot_preprocess_output(
    id: str,
    fn: Callable[[Any], Any] | Callable[[Any], Awaitable[Any]],
) -> None:
    """
    Set a function for preprocessing an output value in test-mode snapshots.

    Uses the current reactive session; equivalent to calling
    `.snapshot_preprocess(fn)` on the renderer object registered for `id`. See
    :meth:`~shiny.render.renderer.Renderer.snapshot_preprocess` for details.
    Inside a module, `id` is resolved in the module's namespace.

    Parameters
    ----------
    id
        The ID of the output.
    fn
        A function (synchronous or asynchronous) that takes the output value
        and returns the value to write to the test snapshot.

    Raises
    ------
    RuntimeError
        If there is no active session.
    ValueError
        If no output with `id` is registered on the session. Call this function
        after defining the output.

    See Also
    --------
    * `shiny.testmode.snapshot_preprocess_input`
    """
    session = require_active_session(None)
    resolved_id = session.output._ns(id)
    output_info = session.output._outputs.get(resolved_id)
    if output_info is None:
        raise ValueError(
            f"No output named {id!r} is registered on this session. "
            "Call `snapshot_preprocess_output()` after defining the output."
        )
    output_info.renderer.snapshot_preprocess(fn)


def _snapshot_preprocess_file_input(value: Any) -> Any:
    """
    Scrub a file-input value for test-mode snapshots.

    Replaces each uploaded file's `datapath` with its basename, since the
    tempdir portion differs on every run (mirrors R's
    `snapshotPreprocessorFileInput`). Auto-registered for file inputs on upload
    and on bookmark restore. Non-list or malformed values pass through
    unchanged.
    """
    if not isinstance(value, list):
        return value
    out: list[Any] = []
    for file_info in value:
        if isinstance(file_info, dict) and isinstance(file_info.get("datapath"), str):
            file_info = {**file_info, "datapath": Path(file_info["datapath"]).name}
        out.append(file_info)
    return out
