"""Collection level management for OpenTelemetry instrumentation."""

from __future__ import annotations

import os
from contextvars import ContextVar
from enum import IntEnum
from typing import Optional

__all__ = ("CollectLevel", "get_collect_level", "should_collect")


class CollectLevel(IntEnum):
    """
    OpenTelemetry collection levels for Shiny instrumentation.

    Collection levels control the granularity of telemetry data collected:

    - NONE (0): No telemetry collected
    - SESSION (1): Session lifecycle spans only
    - REACTIVE_UPDATE (2): SESSION + reactive flush cycles
    - REACTIVITY (3): REACTIVE_UPDATE + individual reactive computations and value updates
    - ALL (4): All available telemetry (currently equivalent to REACTIVITY)

    Examples
    --------
    Set collection level via environment variable:
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


# Context variable to track current collection level
_current_collect_level: ContextVar[Optional[CollectLevel]] = ContextVar(
    "otel_collect_level", default=None
)


def get_collect_level() -> CollectLevel:
    """
    Get the current OpenTelemetry collection level.

    The collection level is determined in the following order:
    1. Context variable (set via otel_collect context manager)
    2. SHINY_OTEL_COLLECT environment variable
    3. Default: ALL

    Returns
    -------
    CollectLevel
        The current collection level.
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
        return CollectLevel[env_level]
    except KeyError:
        # Invalid level, default to ALL
        import warnings

        warnings.warn(
            f"Invalid SHINY_OTEL_COLLECT value: {env_level}. "
            f"Valid values are: {', '.join(level.name.lower() for level in CollectLevel)}. "
            f"Defaulting to 'all'.",
            UserWarning,
            stacklevel=2,
        )
        return CollectLevel.ALL


def should_collect(required_level: CollectLevel) -> bool:
    """
    Check if telemetry should be collected for the given level.

    This combines two checks:
    1. Is OpenTelemetry SDK configured? (via is_tracing_enabled)
    2. Is the current collection level >= required level?

    Parameters
    ----------
    required_level
        The minimum collection level required for this telemetry.

    Returns
    -------
    bool
        True if telemetry should be collected, False otherwise.

    Examples
    --------
    ```python
    from shiny.otel import should_collect, CollectLevel

    if should_collect(CollectLevel.SESSION):
        # Create session span
        pass
    ```
    """
    from ._core import is_tracing_enabled

    if not is_tracing_enabled():
        return False

    return get_collect_level() >= required_level
