from __future__ import annotations

import logging
import os
import re
import typing
from ipaddress import ip_address
from subprocess import run
from typing import Pattern
from urllib.parse import ParseResult, urlparse


def is_workbench() -> bool:
    return bool(os.getenv("RS_SERVER_URL") and os.getenv("RS_SESSION_URL"))


def is_codespaces() -> bool:
    # See https://docs.github.com/en/codespaces/developing-in-a-codespace/default-environment-variables-for-your-codespace
    return bool(
        os.getenv("CODESPACES")
        and os.getenv("CODESPACE_NAME")
        and os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
    )


def is_proxy_env() -> bool:
    return is_workbench() or is_codespaces()


port_cache: dict[int, str] = {}


def get_proxy_url(url: str) -> str:
    if not is_proxy_env():
        return url

    # Regardless of proxying strategy, we don't want to proxy URLs that are not loopback
    parts = urlparse(url)
    is_loopback = parts.hostname == "localhost"
    if not is_loopback:
        try:
            is_loopback = ip_address(parts.hostname or "").is_loopback
        except ValueError:
            pass
    if not is_loopback:
        return url

    # Regardless of proxying strategy, we need to know the port, whether explicit or
    # implicit (from the scheme)
    if parts.port is not None:
        if parts.port == 0:
            # Not sure if this is even legal but we're definitely not going to succeed
            # in proxying it
            return url
        port = parts.port
    elif parts.scheme.lower() in ["ws", "http"]:
        port = 80
    elif parts.scheme.lower() in ["wss", "https"]:
        port = 443
    else:
        # No idea what kind of URL this is
        return url

    if is_workbench():
        return _get_proxy_url_workbench(parts, port) or url
    if is_codespaces():
        return _get_proxy_url_codespaces(parts, port) or url
    return url


def _get_proxy_url_codespaces(parts: ParseResult, port: int) -> str | None:
    # See https://docs.github.com/en/codespaces/developing-in-a-codespace/default-environment-variables-for-your-codespace
    codespace_name = os.getenv("CODESPACE_NAME")
    port_forwarding_domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
    netloc = f"{codespace_name}-{port}.{port_forwarding_domain}"
    if parts.scheme.lower() in ["ws", "wss"]:
        scheme = "wss"
    elif parts.scheme.lower() in ["http", "https"]:
        scheme = "https"
    else:
        return None

    return parts._replace(scheme=scheme, netloc=netloc).geturl()


def _get_proxy_url_workbench(parts: ParseResult, port: int) -> str | None:
    path = parts.path or "/"

    server_url = os.getenv("RS_SERVER_URL", "")
    session_url = os.getenv("RS_SESSION_URL", "")

    if parts.scheme.lower() in ["ws", "wss"]:
        server_url = re.sub("^http", "ws", server_url)
    server_url = re.sub("/$", "", server_url)
    session_url = re.sub("^/", "", session_url)

    if port in port_cache:
        ptoken = port_cache[port]
    else:
        try:
            res = run(
                ["/usr/lib/rstudio-server/bin/rserver-url", str(port)],
                capture_output=True,
                encoding="ascii",
            )
        except FileNotFoundError:
            return None
        if res.returncode != 0:
            return None
        ptoken = res.stdout
        port_cache[port] = ptoken

    return f"{server_url}/{session_url}p/{ptoken}{path}{'?' if parts.query else ''}{parts.query}"


pat_local_url: Pattern[str] = re.compile(
    "https?://(127.0.0.1|localhost)(:\\d+)?([-\\+=&;%@.\\w_]*)", re.IGNORECASE
)


class ProxyUrlFilter:
    def __init__(self):
        pass

    def filter(self, record: logging.LogRecord) -> int:
        record.msg = pat_local_url.sub(self.url_replacement, record.getMessage())
        if hasattr(record, "color_message"):
            color_msg = str(record.color_message)  # type: ignore
            if record.args:
                color_msg = color_msg % record.args
            record.color_message = pat_local_url.sub(  # type: ignore
                self.url_replacement, color_msg
            )
        record.args = ()
        return 1

    def url_replacement(self, match: typing.Match[str]) -> str:
        return get_proxy_url(match.group(0))
