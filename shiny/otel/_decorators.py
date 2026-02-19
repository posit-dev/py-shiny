"""
User-facing decorators and context managers for OpenTelemetry collection control.
"""

from __future__ import annotations

import functools
from contextlib import contextmanager
from typing import Any, Callable, Literal, TypeVar

from ._collect import OtelCollectLevel, _current_collect_level
from ._function_attrs import set_otel_collect_level_on_func

__all__ = ("otel_collect", "no_otel_collect")

T = TypeVar("T")


class OtelCollect:
    """
    Helper class that can be used as both context manager and decorator.

    This class wraps the collection level management functionality, allowing
    the same object to be used with `with` statements or as a function decorator.
    """

    def __init__(
        self,
        level: OtelCollectLevel,
    ) -> None:
        self.level = level
        self._context: Any = None

    def __enter__(self) -> None:
        @contextmanager
        def _context_manager():  # type: ignore[misc]
            """Context manager implementation."""
            token = _current_collect_level.set(self.level)
            try:
                yield
            finally:
                _current_collect_level.reset(token)

        self._context = _context_manager()
        return self._context.__enter__()

    def __exit__(self, *args: Any) -> Any:
        return self._context.__exit__(*args)

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator implementation."""
        # Mark the function with the desired collection level.
        # This will be read by reactive objects (Calc_, Effect_) when they
        # create spans for their execution.
        set_otel_collect_level_on_func(func, self.level)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Also set the context variable for non-reactive uses
            # (e.g., regular functions decorated with @otel_collect)
            @contextmanager
            def _context_manager():  # type: ignore[misc]
                token = _current_collect_level.set(self.level)
                try:
                    yield
                finally:
                    _current_collect_level.reset(token)

            with _context_manager():
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]


def otel_collect(
    level: Literal["none", "session", "reactive_update", "reactivity", "all"],
) -> OtelCollect:
    """
    Control Shiny's OpenTelemetry collection level for a block of code or function.

    This can be used as either a context manager or a decorator to temporarily
    set the collection level for **Shiny's internal telemetry only**, overriding
    the default level from the `SHINY_OTEL_COLLECT` environment variable.

    Note: This only affects spans and logs created by Shiny itself (session lifecycle,
    reactive execution, value updates, etc.). Any OpenTelemetry spans you create
    manually in your application code are unaffected and will continue to be
    recorded normally.

    Parameters
    ----------
    level
        Collection level to use. Must be one of: `"none"`, `"session"`,
        `"reactive_update"`, `"reactivity"`, or `"all"`.

    Returns
    -------
    OtelCollect
        A context manager when used with `with` statement, or a decorator when
        applied to a function.

    Examples
    --------
    **As a context manager:**

    ```python
    from shiny import otel_collect

    # Disable telemetry for a specific block
    with otel_collect("none"):
        # No telemetry collected in this block
        my_value = reactive.value(0)
        my_value.set(10)
    ```

    **As a decorator:**

    ```python
    from shiny import otel_collect

    @otel_collect("none")
    def expensive_computation():
        # No telemetry collected when this function runs
        result = do_something()
        return result
    ```

    **Nested context managers:**

    ```python
    from shiny import otel_collect

    with otel_collect("session"):
        # Only session-level telemetry collected
        with otel_collect("none"):
            # No telemetry collected in this inner block
            do_something()
        # Back to session-level collection
    ```

    **Available collection levels:**

    - `"none"`: No telemetry collected
    - `"session"`: Session lifecycle spans only
    - `"reactive_update"`: Session + reactive update cycles
    - `"reactivity"`: Session + reactive cycles + individual reactive executions and value logs
    - `"all"`: All telemetry (same as `"reactivity"` currently)

    See Also
    --------
    * `shiny.otel.OtelCollectLevel` - Enum defining collection levels (internal use)
    """
    # Validate type
    if not isinstance(level, str):
        raise TypeError(
            f"level must be a string, got {type(level).__name__}"
        )

    # Convert string to enum
    try:
        enum_level = OtelCollectLevel[level.upper()]
    except KeyError:
        valid_levels = ", ".join(f'"{lvl}"' for lvl in ["none", "session", "reactive_update", "reactivity", "all"])
        raise ValueError(
            f"Invalid collection level: {level!r}. "
            f"Valid levels are: {valid_levels}"
        )

    return OtelCollect(enum_level)


def no_otel_collect() -> OtelCollect:
    """
    Disable Shiny's OpenTelemetry collection for a block of code or function.

    This is a convenience function equivalent to `otel_collect("none")`. It can be
    used as either a context manager or a decorator to temporarily disable all
    **Shiny internal telemetry** collection.

    Note: This only affects spans and logs created by Shiny itself. Any OpenTelemetry
    spans you create manually in your application code are unaffected.

    Returns
    -------
    OtelCollect
        A context manager when used with `with` statement, or a decorator when
        applied to a function.

    Examples
    --------
    **As a context manager:**

    ```python
    from shiny.otel import no_otel_collect

    # Disable telemetry for sensitive operations
    with no_otel_collect():
        # No telemetry collected in this block
        api_key = load_secret()
        process_sensitive_data(api_key)
    ```

    **As a decorator:**

    ```python
    from shiny.otel import no_otel_collect

    @no_otel_collect()
    def handle_passwords():
        # No telemetry collected when this function runs
        validate_and_store_password()
    ```

    **Common use cases:**

    - Processing sensitive data (passwords, API keys, PII)
    - High-frequency operations where telemetry overhead matters
    - Compliance requirements to avoid sending certain data to external systems

    See Also
    --------
    * `shiny.otel.otel_collect` - Full control over collection levels
    * `shiny.otel.OtelCollectLevel` - Enum defining all collection levels
    """
    return otel_collect("none")
