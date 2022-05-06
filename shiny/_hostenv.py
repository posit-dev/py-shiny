import os
import re
from ipaddress import ip_address
from subprocess import run
from urllib.parse import urlparse

def is_workbench() -> bool:
    return bool(os.getenv("RS_SERVER_URL") and os.getenv("RS_SESSION_URL"))

def is_proxy_env() -> bool:
    return is_workbench()

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

    server_url = os.getenv("RS_SERVER_URL", "")
    session_url = os.getenv("RS_SESSION_URL", "")

    if parts.scheme.lower() in ["ws", "wss"]:
        server_url = re.sub("^http", "ws", server_url)
    server_url = re.sub("/$", "", server_url)
    session_url = re.sub("^/", "", session_url)

    port = parts.port if parts.port else 80 if parts.scheme in ["ws", "http"] else 443 if parts.scheme in ["wss", "https"] else 0
    if port == 0:
        return url

    try:
        res = run(["/usr/lib/rstudio-server/bin/rserver-url",
            str(port)],
            capture_output=True,
            encoding="ascii")
    except FileNotFoundError:
        return url

    if res.returncode != 0:
        return url

    return f"{server_url}/{session_url}p/{res.stdout}{parts.path}{'?' if parts.query else ''}{parts.query}"
