"""Test-mode tools (see `SHINY_TESTMODE`)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Awaitable, Callable, cast

from ._docstring import add_example

# Import from `shiny.session._utils` directly (not the `shiny.session` package
# __init__): `shiny.session._session` imports from this module, so importing the
# package here would be circular.
from .session._utils import require_active_session

__all__ = (
    "export_test_values",
    "snapshot_preprocess_input",
)


@add_example()
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

    See Also
    --------
    * :func:`~shiny.testmode.snapshot_preprocess_input`
    * :meth:`~shiny.render.renderer.Renderer.snapshot_preprocess`
    * :class:`~shiny.playwright.controller.AppTestValues`
    """
    session = require_active_session(None)
    session._export_test_values(**kwargs)


@add_example()
def snapshot_preprocess_input(
    id: str,
    fn: Callable[[Any], Any] | Callable[[Any], Awaitable[Any]],
) -> None:
    """
    Set a function for preprocessing an input value in test-mode snapshots.

    Uses the current reactive session; equivalent to
    `session.input.set_snapshot_preprocess(id, fn)`. See
    `shiny.session.Inputs.set_snapshot_preprocess` for details. Inside a
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
    * :meth:`~shiny.render.renderer.Renderer.snapshot_preprocess`
    * :func:`~shiny.testmode.export_test_values`
    * :class:`~shiny.playwright.controller.AppTestValues`
    """
    session = require_active_session(None)
    session.input.set_snapshot_preprocess(id, fn)


# NOTE: There is deliberately no `snapshot_preprocess_output(id, fn)` free function
# (the analog of R's `snapshotPreprocessOutput`). Output preprocessors belong to the
# renderer object itself: call `my_output.snapshot_preprocess(fn)` on the
# `@render.*` object. An id-keyed free function would have to look up the
# registered renderer on the current session, which only works after the output is
# registered (order-dependent) and duplicates the method with worse ergonomics.
# Inputs have no author-side object to attach to, hence the free function above.


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
    files = cast("list[Any]", value)
    out: list[Any] = []
    for file_info in files:
        if isinstance(file_info, dict):
            file_dict = cast("dict[str, Any]", file_info)
            datapath = file_dict.get("datapath")
            if isinstance(datapath, str):
                file_info = {**file_dict, "datapath": Path(datapath).name}
        out.append(file_info)
    return out
