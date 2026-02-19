"""
Helper functions for managing OpenTelemetry attributes on function objects.

These functions allow marking functions with metadata that affects how their
execution is traced by OpenTelemetry.
"""

from __future__ import annotations

from typing import Any, Callable

from ._collect import OtelCollectLevel, get_otel_collect_level
from ._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

__all__ = (
    "resolve_func_otel_level",
    "set_otel_collect_level_on_func",
)


def resolve_func_otel_level(
    func: Callable[..., Any],
    default: OtelCollectLevel | None = None,
) -> OtelCollectLevel:
    """
    Resolve the OTel collection level for a function with automatic fallback.

    Checks the function for an @otel_collect decorator attribute, then falls
    back to the provided default, or finally to the current context level.

    Parameters
    ----------
    func
        The function to resolve the collection level for.
    default
        Default level if no decorator is present on the function.
        If None (default), falls back to the current context level.

    Returns
    -------
    OtelCollectLevel
        The resolved collection level from function attribute, default, or context.

    Notes
    -----
    This attribute is set by the @otel_collect() decorator and is automatically
    preserved through decorator chains when functools.wraps is used.

    Reactive objects (Calc_, Effect_) check for this attribute to determine
    what collection level to use when creating spans for their execution.

    Examples
    --------
    ```python
    # Automatically uses context level as fallback
    level = resolve_func_otel_level(fn)

    # Or provide a custom default
    level = resolve_func_otel_level(fn, default=OtelCollectLevel.SESSION)
    ```
    """
    func_level = getattr(func, FUNC_ATTR_OTEL_COLLECT_LEVEL, None)

    if func_level is not None:
        return func_level

    if default is not None:
        return default

    return get_otel_collect_level()


def set_otel_collect_level_on_func(
    func: Callable[..., Any], level: OtelCollectLevel
) -> None:
    """
    Set the OTel collection level on a function object.

    This is used by the @otel_collect decorator to mark functions with their
    desired collection level. The level will be used when the function is
    executed as part of a reactive context (Calc, Effect, etc.).

    Parameters
    ----------
    func
        The function to set the collection level on.
    level
        The collection level to use for this function's execution.

    Notes
    -----
    This function modifies the function object in-place by setting an attribute
    on its __dict__. When functools.wraps is used in decorators, the __dict__
    is automatically copied from the original function to the wrapper, which
    preserves this attribute through decorator chains.
    """
    setattr(func, FUNC_ATTR_OTEL_COLLECT_LEVEL, level)
