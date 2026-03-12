"""Collect level management for OpenTelemetry instrumentation."""

from __future__ import annotations

import os
from contextvars import ContextVar
from enum import IntEnum
from typing import Optional

__all__ = ("OtelCollectLevel", "get_level")


class OtelCollectLevel(IntEnum):
    """
    OpenTelemetry collect levels for Shiny instrumentation.

    Collect levels control the granularity of telemetry data collected:

    - NONE: No telemetry collected
    - SESSION: Session lifecycle spans only
    - REACTIVE_UPDATE: SESSION + reactive update cycles
    - REACTIVITY: REACTIVE_UPDATE + individual reactive executions and value updates
    - ALL: All available telemetry (currently equivalent to REACTIVITY)

    Examples
    --------
    Set collect level via environment variable:
    ```bash
    export SHINY_OTEL_COLLECT=session
    python app.py
    ```

    Or suppress telemetry programmatically:
    ```python
    from shiny import otel

    with otel.suppress():
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


def _get_env_level() -> OtelCollectLevel:
    """Read the collection level from the env var only, bypassing the contextvar.

    Used by infrastructure spans (session_start, session_end, reactive_update)
    that must not be affected by otel.suppress() or otel.collect().
    """
    env_level = os.getenv("SHINY_OTEL_COLLECT", "all").strip().upper()

    try:
        return OtelCollectLevel[env_level]
    except KeyError:
        import warnings

        warnings.warn(
            f"Invalid SHINY_OTEL_COLLECT value: {env_level}. "
            f"Valid values are: {', '.join(level.name.lower() for level in OtelCollectLevel)}. "
            f"Defaulting to 'all'.",
            UserWarning,
            stacklevel=2,
        )
        return OtelCollectLevel.ALL


def get_level() -> OtelCollectLevel:
    """
    Get the current OpenTelemetry collect level.

    The collect level is determined in the following order:
    1. Context variable (set via ``otel.suppress()`` context manager)
    2. SHINY_OTEL_COLLECT environment variable
    3. Default: ALL

    Returns
    -------
    OtelCollectLevel
        The current collect level.

    Examples
    --------
    Check the current collection level:

    ```python
    from shiny import otel

    # Get the current level
    level = otel.get_level()
    print(f"Current level: {level.name}")  # e.g., "ALL", "SESSION", "NONE"
    ```

    Use with suppress context manager:

    ```python
    from shiny import otel

    print(otel.get_level().name)  # "ALL" (default)

    with otel.suppress():
        print(otel.get_level().name)  # "NONE"

    print(otel.get_level().name)  # "ALL" (restored)
    ```
    """
    # Check context variable first (set by otel.suppress() context manager)
    level = _current_collect_level.get()
    if level is not None:
        return level

    return _get_env_level()
