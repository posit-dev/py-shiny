from __future__ import annotations

from collections.abc import Mapping

TRACE_VERSION = 1
"""Version of the portable Reactlog trace format."""


def check_trace_version(trace: Mapping[str, object]) -> None:
    """Raise ValueError for a trace with an explicit, unsupported format version."""
    version = trace.get("trace_version", TRACE_VERSION)
    if isinstance(version, bool) or version != TRACE_VERSION:
        raise ValueError(f"Unsupported Reactlog trace version: {version}")
