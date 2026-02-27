"""
User-facing decorators and context managers for OpenTelemetry collection control.
"""

from __future__ import annotations

from contextvars import Token
from typing import Any, Callable, Literal, TypeVar

from ._collect import OtelCollectLevel, _current_collect_level
from ._function_attrs import set_otel_collect_level_on_func

__all__ = ("otel_collect", "no_otel_collect")

T = TypeVar("T")


class OtelCollect:
    """
    Helper class that can be used as both context manager and decorator.

    This class wraps the collect level management functionality, allowing
    the same object to be used with `with` statements or as a function decorator.
    """

    def __init__(
        self,
        level: OtelCollectLevel,
    ) -> None:
        self.level = level
        self._token: Token[OtelCollectLevel | None] | None = None

    def __enter__(self) -> None:
        """Set the collect level for the duration of the context."""
        self._token = _current_collect_level.set(self.level)
        return None

    def __exit__(self, *args: Any) -> None:
        """Reset the collect level to its previous value."""
        if self._token is not None:
            _current_collect_level.reset(self._token)
            self._token = None

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator implementation."""
        # Reject reactive objects - otel_collect should decorate functions, not objects
        from shiny.reactive._reactives import Calc_, Effect_
        from shiny.render.renderer import Renderer

        if isinstance(func, Calc_):
            raise TypeError(
                f"otel_collect() cannot be used on @reactive.calc objects. "
                f"Apply @otel_collect before @reactive.calc:\n"
                f"  @reactive.calc\n"
                f'  @otel_collect("{self.level.name.lower()}")\n'
                f"  def my_calc(): ..."
            )

        if isinstance(func, Effect_):
            raise TypeError(
                f"otel_collect() cannot be used on @reactive.effect objects. "
                f"Apply @otel_collect before @reactive.effect:\n"
                f"  @reactive.effect\n"
                f'  @otel_collect("{self.level.name.lower()}")\n'
                f"  def my_effect(): ..."
            )

        if isinstance(func, Renderer):
            raise TypeError(
                f"otel_collect() cannot be used on render objects. "
                f"Apply @otel_collect before the @render.func decorator:\n"
                f"  @render.text  # or @render.plot, etc.\n"
                f'  @otel_collect("{self.level.name.lower()}")\n'
                f"  def my_output(): ..."
            )

        # Mark the function with the desired collect level.
        # This will be read by reactive objects (Calc_, Effect_) when they
        # create spans for their execution.
        set_otel_collect_level_on_func(func, self.level)
        return func


def otel_collect(
    level: Literal["none", "session", "reactive_update", "reactivity", "all"],
) -> OtelCollect:
    """
    Control Shiny's OpenTelemetry collect level for a block of code or function.

    This can be used as either a context manager or a decorator to temporarily
    set the collect level for **Shiny's internal telemetry only**, overriding
    the default level from the `SHINY_OTEL_COLLECT` environment variable.

    Note: This only affects spans and logs created by Shiny itself (session lifecycle,
    reactive execution, value updates, etc.). Any OpenTelemetry spans you create
    manually in your application code are unaffected and will continue to be
    recorded normally.

    Parameters
    ----------
    level
        Collect level to use. Must be one of: `"none"`, `"session"`,
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
    from shiny.otel import otel_collect

    # Disable telemetry for a specific block
    with otel_collect("none"):
        # No telemetry collected in this block
        my_value = reactive.value(0)
        my_value.set(10)
    ```

    **As a decorator:**

    ```python
    from shiny.otel import otel_collect

    @otel_collect("none")
    def expensive_computation():
        # No telemetry collected when this function runs
        result = do_something()
        return result
    ```

    **Nested context managers:**

    ```python
    from shiny.otel import otel_collect

    with otel_collect("session"):
        # Only session-level telemetry collected
        with otel_collect("none"):
            # No telemetry collected in this inner block
            do_something()
        # Back to session-level collection
    ```

    **Available collect levels:**

    - `"none"`: No telemetry collected
    - `"session"`: Session lifecycle spans only
    - `"reactive_update"`: Session + reactive update cycles
    - `"reactivity"`: Session + reactive cycles + individual reactive executions and value logs
    - `"all"`: All telemetry (same as `"reactivity"` currently)

    See Also
    --------
    * `shiny.otel.OtelCollectLevel` - Enum defining collect levels (internal use)
    """
    # Validate type
    if not isinstance(level, str):
        raise TypeError(f"level must be a string, got {type(level).__name__}")

    # Enforce lowercase (matching Literal type hint)
    valid_levels_list = ["none", "session", "reactive_update", "reactivity", "all"]
    if level not in valid_levels_list:
        valid_levels = ", ".join(f'"{lvl}"' for lvl in valid_levels_list)
        raise ValueError(
            f"Invalid collect level: {level!r}. "
            f"Valid levels are: {valid_levels} (must be lowercase)"
        )

    # Convert string to enum (now guaranteed to be valid lowercase)
    enum_level = OtelCollectLevel[level.upper()]

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
    * `shiny.otel.otel_collect` - Full control over collect levels
    * `shiny.otel.OtelCollectLevel` - Enum defining all collect levels
    """
    return otel_collect("none")
