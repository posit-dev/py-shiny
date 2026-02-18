"""
Helper functions for managing OpenTelemetry attributes on function objects.

These functions allow marking functions with metadata that affects how their
execution is traced by OpenTelemetry.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from ._collect import OtelCollectLevel
from ._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

__all__ = (
    "get_otel_collect_level_from_func",
    "set_otel_collect_level_on_func",
)


def get_otel_collect_level_from_func(
    func: Callable[..., Any],
) -> Optional[OtelCollectLevel]:
    """
    Get the OTel collection level set on a function by @otel_collect decorator.

    Parameters
    ----------
    func
        The function to retrieve the collection level from.

    Returns
    -------
    OtelCollectLevel | None
        The collection level if set, or None if no level has been set.

    Notes
    -----
    This attribute is set by the @otel_collect() decorator and is automatically
    preserved through decorator chains when functools.wraps is used.

    Reactive objects (Calc_, Effect_) check for this attribute to determine
    what collection level to use when creating spans for their execution.
    """
    return getattr(func, FUNC_ATTR_OTEL_COLLECT_LEVEL, None)


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
