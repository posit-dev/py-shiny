"""HTTP and session attribute extraction for OpenTelemetry spans."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, Dict, cast


if TYPE_CHECKING:
    from starlette.requests import HTTPConnection

__all__ = ("extract_http_attributes", "extract_source_ref")


def extract_http_attributes(http_conn: HTTPConnection) -> Dict[str, Any]:
    """
    Extract HTTP attributes from an HTTP connection for OTel spans.

    This extracts standard HTTP semantic attributes following OpenTelemetry
    semantic conventions for HTTP.

    Parameters
    ----------
    http_conn
        The HTTP connection object from the session.

    Returns
    -------
    Dict[str, Any]
        Dictionary of HTTP attributes suitable for span attributes.

    Examples
    --------
    ```python
    from shiny.otel._attributes import extract_http_attributes

    # In session context
    http_attrs = extract_http_attributes(session.http_conn)
    # Returns: {
    #     "server.address": "localhost",
    #     "server.port": 8000,
    #     "url.path": "/",
    #     "url.scheme": "http"
    # }
    ```

    Notes
    -----
    Following OTel semantic conventions:
    - `server.address`: Host name or IP address
    - `server.port`: Port number
    - `url.path`: Request path
    - `url.scheme`: Protocol scheme (http, https, ws, wss)
    """
    attributes: Dict[str, Any] = {}

    # Extract server address (hostname)
    if hasattr(http_conn, "url") and http_conn.url:
        if http_conn.url.hostname:
            attributes["server.address"] = http_conn.url.hostname
        if http_conn.url.port:
            attributes["server.port"] = http_conn.url.port
        if http_conn.url.path:
            attributes["url.path"] = http_conn.url.path
        if http_conn.url.scheme:
            attributes["url.scheme"] = http_conn.url.scheme

    # Fallback: try to extract from scope (ASGI)
    if not attributes and hasattr(http_conn, "scope"):
        scope = http_conn.scope
        if "server" in scope and scope["server"]:
            server_tuple = scope["server"]
            if isinstance(server_tuple, (list, tuple)) and len(server_tuple) >= 2:  # type: ignore[arg-type]
                # ASGI scope server is tuple[str, int | None]
                server_host = cast(str, server_tuple[0])
                server_port = cast(int, server_tuple[1])
                if server_host:
                    attributes["server.address"] = server_host
                if server_port:
                    attributes["server.port"] = server_port
        if "path" in scope:
            attributes["url.path"] = scope["path"]
        if "scheme" in scope:
            attributes["url.scheme"] = scope["scheme"]

    return attributes


def extract_source_ref(func: Callable[..., Any]) -> Dict[str, Any]:
    """
    Extract source code location attributes from a function for OTel spans.

    This extracts source file path, line number, and function name following
    OpenTelemetry semantic conventions for code attributes.

    Parameters
    ----------
    func
        The function to extract source information from.

    Returns
    -------
    Dict[str, Any]
        Dictionary of source code attributes suitable for span attributes.
        Returns empty dict if source information is unavailable.

    Examples
    --------
    ```python
    from shiny.otel._attributes import extract_source_ref

    def my_calc():
        return 42

    attrs = extract_source_ref(my_calc)
    # Returns: {
    #     "code.filepath": "/path/to/file.py",
    #     "code.lineno": 42,
    #     "code.function": "my_calc"
    # }
    ```

    Notes
    -----
    Following OTel semantic conventions:
    - `code.filepath`: Full path to source file
    - `code.lineno`: Line number where function is defined
    - `code.function`: Function name

    Source information may not be available for:
    - Built-in functions
    - Functions defined in C extensions
    - Dynamically generated functions
    - Lambda functions (will have name "<lambda>")
    """
    attributes: Dict[str, Any] = {}

    # Get source file path
    try:
        source_file = inspect.getsourcefile(func)
        if source_file:
            attributes["code.filepath"] = source_file
    except (TypeError, OSError):
        # TypeError: built-in functions, C extensions
        # OSError: source file not found
        pass

    # Get line number where function is defined
    try:
        source_lines = inspect.getsourcelines(func)
        if source_lines:
            # getsourcelines returns (lines, starting_line_number)
            line_number = source_lines[1]
            attributes["code.lineno"] = line_number
    except (TypeError, OSError):
        # TypeError: built-in functions, C extensions
        # OSError: source file not found
        pass

    # Get function name (this rarely fails)
    func_name = getattr(func, "__name__", None)
    if func_name:
        attributes["code.function"] = func_name

    return attributes
