"""Test-mode value exporting (see `SHINY_TESTMODE`)."""

from __future__ import annotations

from typing import Any, Callable

from .session import require_active_session

__all__ = ("export_test_values",)


def export_test_values(**kwargs: Callable[[], Any]) -> None:
    """
    Register named values to include in the test-mode snapshot.

    This is the module-level counterpart to
    `shiny.Session.export_test_values`. It uses the current reactive session.
    Each value must be a zero-argument callable (a plain function/`lambda` or a
    `reactive.calc`); it is evaluated lazily, in a reactive isolate, when a test
    snapshot is requested. Registered values appear under the `export` block of
    the snapshot served at `/session/{id}/dataobj/shinytest`.

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
    * `shiny.Session.export_test_values`
    """
    session = require_active_session(None)
    session.export_test_values(**kwargs)
