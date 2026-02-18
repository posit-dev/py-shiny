"""
OpenTelemetry constants for Shiny.

This module contains all named constants used throughout the otel submodule,
including attribute names, span names, and configuration values.
"""

__all__ = (
    # Tracer configuration
    "TRACER_NAME",
    # Attribute names - Session
    "ATTR_SESSION_ID",
    # Exception attributes
    "EXCEPTION_ATTR_OTEL_RECORDED",
    # Function attributes
    "FUNC_ATTR_OTEL_LABEL_MODIFIER",
    "FUNC_ATTR_OTEL_COLLECT_LEVEL",
)

# ============================================================================
# Tracer Configuration
# ============================================================================

TRACER_NAME = "co.posit.python-package.shiny"
"""The tracer name used for all Shiny OpenTelemetry spans."""

# ============================================================================
# OpenTelemetry Semantic Convention Attributes
# ============================================================================
# Following: https://opentelemetry.io/docs/specs/semconv/

# Session Attributes
# ------------------

ATTR_SESSION_ID = "session.id"
"""The unique identifier for a Shiny session."""

# ============================================================================
# Exception Object Attributes
# ============================================================================

EXCEPTION_ATTR_OTEL_RECORDED = "_shiny_otel_exception_recorded"
"""
Attribute name used to mark exceptions as recorded in OpenTelemetry spans.

This prevents the same exception from being recorded multiple times as it
propagates through parent spans.
"""

# ============================================================================
# Function Object Attributes
# ============================================================================

FUNC_ATTR_OTEL_LABEL_MODIFIER = "_shiny_otel_label_modifier"
"""Attribute name used to store OTel label modifiers on function objects."""

FUNC_ATTR_OTEL_COLLECT_LEVEL = "_shiny_otel_collect_level"
"""Attribute name used to store OTel collection level on function objects."""
