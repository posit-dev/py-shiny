from __future__ import annotations

import logging
import os
import re
import typing
from ipaddress import ip_address
from subprocess import run
from typing import Pattern
from urllib.parse import urlparse


def is_workbench() -> bool:
    return bool(os.getenv("RS_SERVER_URL") and os.getenv("RS_SESSION_URL"))


def is_proxy_env() -> bool:
    return is_workbench()


port_cache: dict[int, str] = {}


def get_proxy_url(url: str) -> str:
    if not is_workbench():
        return url

    parts = urlparse(url)
    is_loopback = parts.hostname == "localhost"
    if not is_loopback:
        try:
            is_loopback = ip_address(parts.hostname or "").is_loopback
        except ValueError:
            pass
    if not is_loopback:
        return url

    path = parts.path or "/"

    server_url = os.getenv("RS_SERVER_URL", "")
    session_url = os.getenv("RS_SESSION_URL", "")

    if parts.scheme.lower() in ["ws", "wss"]:
        server_url = re.sub("^http", "ws", server_url)
    server_url = re.sub("/$", "", server_url)
    session_url = re.sub("^/", "", session_url)

    port = (
        parts.port
        if parts.port
        else 80
        if parts.scheme in ["ws", "http"]
        else 443
        if parts.scheme in ["wss", "https"]
        else 0
    )
    if port == 0:
        return url

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
            return url
        if res.returncode != 0:
            return url
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
