"""
Error handling and sanitization for OpenTelemetry spans.

This module provides utilities for recording exceptions in OpenTelemetry spans
while respecting Shiny's error sanitization and silent exception semantics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import Session

__all__ = (
    "is_silent_error",
    "should_sanitize_errors",
    "maybe_sanitize_error",
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
    from ..types import (
        SilentCancelOutputException,
        SilentException,
        SilentOperationInProgressException,
    )

    return isinstance(
        exception,
        (SilentException, SilentCancelOutputException, SilentOperationInProgressException),
    )


def should_sanitize_errors(session: Session | None = None) -> bool:
    """
    Check if error messages should be sanitized based on app settings.

    When sanitization is enabled, exception messages are replaced with a generic
    message to avoid leaking sensitive information in production environments.

    Parameters
    ----------
    session
        The current session. If None, attempts to get the current session from context.
        If no session is available, returns False (no sanitization).

    Returns
    -------
    bool
        True if errors should be sanitized, False otherwise.

    Examples
    --------
    >>> from shiny import App
    >>> from shiny.session import get_current_session
    >>> # In a Shiny app context:
    >>> session = get_current_session()
    >>> should_sanitize_errors(session)
    False  # Default is False

    Notes
    -----
    Error sanitization is controlled by the `App.sanitize_errors` setting, which
    may be enabled by default in production environments like Posit Connect.

    `SafeException` messages bypass sanitization even when this setting is True.

    See Also
    --------
    - `shiny.types.SafeException`
    - `maybe_sanitize_error`
    """
    if session is None:
        # Try to get current session from context
        try:
            from ..session import get_current_session

            session = get_current_session()
        except LookupError:
            # No session context, don't sanitize
            return False

    # Session might still be None if get_current_session() returned None
    if session is None:
        return False

    return session.app.sanitize_errors


def maybe_sanitize_error(
    exception: Exception, session: Session | None = None
) -> Exception:
    """
    Sanitize an exception message if required by app settings.

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

    See Also
    --------
    - `should_sanitize_errors`
    - `shiny.types.SafeException`
    """
    from ..types import SafeException

    # SafeException always bypasses sanitization
    if isinstance(exception, SafeException):
        return exception

    # Check if we should sanitize
    if not should_sanitize_errors(session):
        return exception

    # Get the generic error message
    if session is None:
        try:
            from ..session import get_current_session

            session = get_current_session()
        except LookupError:
            # No session, return original
            return exception

    # Session might still be None if get_current_session() returned None
    if session is None:
        return exception

    # Create a new exception with the generic message
    # Preserve the exception type so error handlers can still work
    sanitized_msg = session.app.sanitize_error_msg
    exc_type = type(exception)

    try:
        # Try to create a new exception of the same type with the sanitized message
        return exc_type(sanitized_msg)
    except Exception:
        # If that fails, just return a generic Exception
        return Exception(sanitized_msg)
