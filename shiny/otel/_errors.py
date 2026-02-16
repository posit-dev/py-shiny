"""
Error handling and sanitization for OpenTelemetry spans.

This module provides utilities for recording exceptions in OpenTelemetry spans
while respecting Shiny's error sanitization and silent exception semantics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..session import get_current_session
from ..types import (
    SafeException,
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)

if TYPE_CHECKING:
    from ..session import Session

__all__ = (
    "is_silent_error",
    "should_sanitize_errors",
    "maybe_sanitize_error",
    "has_otel_exception_been_recorded",
    "mark_otel_exception_as_recorded",
)


def is_silent_error(exception: Exception) -> bool:
    """
    Check if an exception is a "silent" exception that should not be recorded.

    Silent exceptions are used in Shiny to halt execution without showing errors
    to users or recording them in logs.

    Parameters
    ----------
    exception
        The exception to check.

    Returns
    -------
    bool
        True if the exception is a silent exception and should not be recorded.

    Examples
    --------
    >>> from shiny.types import SilentException, SilentCancelOutputException
    >>> is_silent_error(SilentException())
    True
    >>> is_silent_error(ValueError("normal error"))
    False

    Notes
    -----
    The following exception types are considered silent:
    - `SilentException`: Pauses execution without showing output
    - `SilentCancelOutputException`: Pauses execution, preserves existing output
    - `SilentOperationInProgressException`: Indicates operation in progress

    See Also
    --------
    - `shiny.types.SilentException`
    - `shiny.types.SilentCancelOutputException`
    - `shiny.types.SilentOperationInProgressException`
    """
    return isinstance(
        exception,
        (
            SilentException,
            SilentCancelOutputException,
            SilentOperationInProgressException,
        ),
    )


def should_sanitize_errors(session: Session | None = None) -> bool:
    """
    Check if error messages should be sanitized for OpenTelemetry based on app settings.

    When sanitization is enabled, exception messages are replaced with a generic
    message to avoid leaking sensitive information to telemetry backends.

    Parameters
    ----------
    session
        The current session. If None, attempts to get the current session from context.
        If no session is available, defaults to True for security.

    Returns
    -------
    bool
        True if errors should be sanitized for OpenTelemetry, False otherwise.

    Examples
    --------
    >>> from shiny import App
    >>> from shiny.session import get_current_session
    >>> # In a Shiny app context:
    >>> session = get_current_session()
    >>> should_sanitize_errors(session)
    True  # Default is True for security

    Notes
    -----
    Error sanitization for OpenTelemetry is controlled by the `App.sanitize_otel_errors`
    setting, which defaults to True to prevent sensitive information from being sent to
    external telemetry backends. This is separate from `App.sanitize_errors` which
    controls UI error messages.

    When no session is available, this function defaults to True as a security precaution.

    `SafeException` messages bypass sanitization even when this setting is True.

    See Also
    --------
    - `shiny.types.SafeException`
    - `maybe_sanitize_error`
    """
    if session is None:
        # Try to get current session from context
        session = get_current_session()

    # Session might still be None if get_current_session() returned None
    if session is None:
        return True

    return session.app.sanitize_otel_errors


def maybe_sanitize_error(
    exception: Exception, session: Session | None = None
) -> Exception:
    """
    Sanitize an exception message for OpenTelemetry if required by app settings.

    This function checks if error sanitization is enabled and if the exception
    is not a `SafeException`. If both conditions are met, it returns a new
    exception with a generic message. Otherwise, it returns the original exception.

    Parameters
    ----------
    exception
        The exception to potentially sanitize.
    session
        The current session. If None, attempts to get the current session from context.

    Returns
    -------
    Exception
        Either the original exception or a sanitized copy with a generic message.

    Examples
    --------
    >>> from shiny.types import SafeException
    >>> # Regular exception (with sanitization enabled):
    >>> exc = ValueError("Database password is 'secret123'")
    >>> sanitized = maybe_sanitize_error(exc)
    >>> str(sanitized)
    'An error has occurred. Check your logs or contact the app author for clarification.'

    >>> # SafeException bypasses sanitization:
    >>> safe_exc = SafeException("This is safe to show")
    >>> result = maybe_sanitize_error(safe_exc)
    >>> str(result)
    'This is safe to show'

    Notes
    -----
    The generic error message is taken from `App.sanitize_error_msg`, which can
    be customized per application.

    `SafeException` exceptions always bypass sanitization, allowing developers
    to generate user-friendly error messages even when sanitization is enabled.

    Error sanitization for OpenTelemetry defaults to True for security. This is
    separate from UI error sanitization (`App.sanitize_errors`).

    See Also
    --------
    - `should_sanitize_errors`
    - `shiny.types.SafeException`
    """
    # SafeException always bypasses sanitization
    if isinstance(exception, SafeException):
        return exception

    # Check if we should sanitize
    if not should_sanitize_errors(session):
        return exception

    # Get the session if not provided
    if session is None:
        session = get_current_session()

    # Get the generic error message
    # If no session is available, use the default message
    if session is None:
        from .._app import SANITIZE_ERROR_MSG

        sanitized_msg = SANITIZE_ERROR_MSG
    else:
        sanitized_msg = session.app.sanitize_error_msg

    # Create a new exception with the generic message
    # Preserve the exception type so error handlers can still work
    exc_type = type(exception)

    try:
        # Try to create a new exception of the same type with the sanitized message
        return exc_type(sanitized_msg)
    except Exception:
        # If that fails, just return a generic Exception
        return Exception(sanitized_msg)


def has_otel_exception_been_recorded(exception: Exception) -> bool:
    """
    Check if an exception has already been recorded in an OTel span.

    This is used to ensure we only record the exception once at the innermost
    span where it originates, not in every parent span it propagates through.

    Parameters
    ----------
    exception
        The exception to check.

    Returns
    -------
    bool
        True if the exception has already been recorded in a span, False otherwise.

    Examples
    --------
    >>> exc = ValueError("Something went wrong")
    >>> has_otel_exception_been_recorded(exc)
    False
    >>> mark_otel_exception_as_recorded(exc)
    >>> has_otel_exception_been_recorded(exc)
    True

    Notes
    -----
    This function checks for a `_shiny_otel_exception_recorded` key in the exception's
    `__dict__`. This key is set by `mark_otel_exception_as_recorded()` when
    the exception is first recorded in a span.

    This pattern matches R Shiny's behavior where exceptions are only recorded
    at the innermost reactive span, while parent spans still get ERROR status.

    See Also
    --------
    - `mark_otel_exception_as_recorded`
    """
    return exception.__dict__.get("_shiny_otel_exception_recorded", False)


def mark_otel_exception_as_recorded(exception: Exception) -> None:
    """
    Mark an exception as having been recorded in an OTel span.

    This prevents the same exception from being recorded multiple times
    as it propagates up through parent spans. All parent spans will still
    get ERROR status, but only the innermost span records the exception details.

    Parameters
    ----------
    exception
        The exception to mark as recorded.

    Examples
    --------
    >>> exc = ValueError("Something went wrong")
    >>> has_otel_exception_been_recorded(exc)
    False
    >>> mark_otel_exception_as_recorded(exc)
    >>> has_otel_exception_been_recorded(exc)
    True

    Notes
    -----
    This function sets a `_shiny_otel_exception_recorded` key in the exception's `__dict__`.
    This key is checked by `has_otel_exception_been_recorded()`.

    This pattern matches R Shiny's behavior where exceptions are only recorded
    at the innermost reactive span, while parent spans still get ERROR status.

    See Also
    --------
    - `has_otel_exception_been_recorded`
    """
    exception.__dict__["_shiny_otel_exception_recorded"] = True
