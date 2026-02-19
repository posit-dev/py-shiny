"""Collect level management for OpenTelemetry instrumentation."""

from __future__ import annotations

import os
from contextvars import ContextVar
from enum import IntEnum
from typing import Optional

__all__ = ("OtelCollectLevel", "get_otel_collect_level", "should_otel_collect")


class OtelCollectLevel(IntEnum):
    """
    OpenTelemetry collect levels for Shiny instrumentation.

    Collect levels control the granularity of telemetry data collected:

    - NONE (0): No telemetry collected
    - SESSION (1): Session lifecycle spans only
    - REACTIVE_UPDATE (2): SESSION + reactive update cycles
    - REACTIVITY (3): REACTIVE_UPDATE + individual reactive executions and value updates
    - ALL (4): All available telemetry (currently equivalent to REACTIVITY)

    Examples
    --------
    Set collect level via environment variable:
    ```bash
    export SHINY_OTEL_COLLECT=session
    python app.py
    ```

    Or programmatically:
    ```python
    from shiny.otel import otel_collect

    with otel_collect("none"):
        # No telemetry in this block
        pass
    ```
    """

    NONE = 0
    SESSION = 1
    REACTIVE_UPDATE = 2
    REACTIVITY = 3
    ALL = 4


# Context variable to track current collect level
_current_collect_level: ContextVar[Optional[OtelCollectLevel]] = ContextVar(
    "otel_collect_level", default=None
)


def get_otel_collect_level() -> OtelCollectLevel:
    """
    Get the current OpenTelemetry collect level.

    The collect level is determined in the following order:
    1. Context variable (set via otel_collect context manager)
    2. SHINY_OTEL_COLLECT environment variable
    3. Default: ALL

    Returns
    -------
    OtelCollectLevel
        The current collect level.
    """
    # Check context variable first (set by otel_collect context manager)
    level = _current_collect_level.get()
    if level is not None:
        return level

    # Check environment variable
    env_level = os.getenv("SHINY_OTEL_COLLECT", "all").strip().upper()

    # Handle common variations
    if env_level == "REACTIVE":
        env_level = "REACTIVITY"

    try:
        return OtelCollectLevel[env_level]
    except KeyError:
        # Invalid level, default to ALL
        import warnings

        warnings.warn(
            f"Invalid SHINY_OTEL_COLLECT value: {env_level}. "
            f"Valid values are: {', '.join(level.name.lower() for level in OtelCollectLevel)}. "
            f"Defaulting to 'all'.",
            UserWarning,
            stacklevel=2,
        )
        return OtelCollectLevel.ALL


def should_otel_collect(required_level: OtelCollectLevel) -> bool:
    """
    Check if telemetry should be collected for the given level.

    This combines two checks:
    1. Is OpenTelemetry SDK configured? (via is_otel_tracing_enabled)
    2. Is the current collect level >= required level?

    Parameters
    ----------
    required_level
        The minimum collect level required for this telemetry.
        Must be one of: SESSION, REACTIVE_UPDATE, REACTIVITY, or ALL.
        NONE is not a valid required level.

    Returns
    -------
    bool
        True if telemetry should be collected, False otherwise.

    Raises
    ------
    ValueError
        If required_level is NONE (NONE is not a valid telemetry level).

    Examples
    --------
    ```python
    from shiny.otel import should_otel_collect, OtelCollectLevel

    if should_otel_collect(OtelCollectLevel.SESSION):
        # Create session span
        pass
    ```
    """
    from ._core import is_otel_tracing_enabled

    # NONE is not a valid required level - it means "no telemetry"
    if required_level == OtelCollectLevel.NONE:
        raise ValueError(
            "should_otel_collect() cannot be called with OtelCollectLevel.NONE. "
            "NONE means no telemetry should be collected. "
            "Use SESSION, REACTIVE_UPDATE, REACTIVITY, or ALL instead."
        )

    if not is_otel_tracing_enabled():
        return False

    return get_otel_collect_level() >= required_level
