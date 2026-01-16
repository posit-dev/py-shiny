"""HTTP and session attribute extraction for OpenTelemetry spans."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from starlette.requests import HTTPConnection

__all__ = ("extract_http_attributes",)


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
            server_host, server_port = scope["server"]
            if server_host:
                attributes["server.address"] = server_host
            if server_port:
                attributes["server.port"] = server_port
        if "path" in scope:
            attributes["url.path"] = scope["path"]
        if "scheme" in scope:
            attributes["url.scheme"] = scope["scheme"]

    return attributes
