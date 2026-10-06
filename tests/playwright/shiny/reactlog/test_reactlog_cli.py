import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller

APP = Path(__file__).parent / "record_app" / "app.py"


def _kill_cli(proc: subprocess.Popen[str]) -> None:
    """SIGTERM stops the CLI and the app (own session) it started; SIGKILL if hung."""
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


def _cleanup(proc: subprocess.Popen[str], port: int | None) -> None:
    """Stop the CLI, then any app server it orphaned (its own session, own port)."""
    _kill_cli(proc)
    if port is None or not _accepts_connections(port) or shutil.which("lsof") is None:
        return
    pids = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"], capture_output=True, text=True
    ).stdout.split()
    for pid in pids:
        os.kill(int(pid), signal.SIGKILL)


def _accepts_connections(port: int) -> bool:
    try:
        socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
    except OSError:
        return False
    return True


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX signals")
def test_reactlog_cli_sigterm_stops_the_app(tmp_path: Path) -> None:
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "shiny",
            "reactlog",
            str(APP),
            "--no-browser",
            "--json",
            str(tmp_path / "o.json"),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    port: int | None = None
    try:
        assert proc.stdout is not None
        first_line = proc.stdout.readline()
        url = re.search(r"http://\S+", first_line)
        assert url is not None, first_line
        port = urlparse(url.group(0)).port
        assert port is not None
        assert _accepts_connections(port)

        proc.terminate()  # the CLI pid only, not its group
        proc.wait(timeout=30)
        deadline = time.time() + 5
        while _accepts_connections(port) and time.time() < deadline:
            time.sleep(0.1)
        assert not _accepts_connections(port), "the app outlived the CLI"
    finally:
        _cleanup(proc, port)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX process groups")
def test_reactlog_cli_no_browser_exports_after_ctrl_c(
    page: Page, tmp_path: Path
) -> None:
    html, out_json = tmp_path / "r.html", tmp_path / "r.json"
    # Its own process group, like a terminal job, so the SIGINT below reaches the
    # CLI and everything it started in that group, as Ctrl+C would.
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "shiny",
            "reactlog",
            str(APP),
            "--no-browser",
            "--html",
            str(html),
            "--json",
            str(out_json),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    port: int | None = None
    try:
        assert proc.stdout is not None
        first_line = proc.stdout.readline()
        url = re.search(r"http://\S+", first_line)
        assert url is not None, first_line
        port = urlparse(url.group(0)).port

        page.goto(url.group(0))
        controller.InputSlider(page, "n").set("7")
        controller.OutputText(page, "out").expect_value("14")
        # A second session: with no terminal to ask, the newest is exported.
        page.reload()
        controller.InputSlider(page, "n").set("4")
        controller.OutputText(page, "out").expect_value("8")
        page.goto("about:blank")  # nothing holds the app open once it is signaled

        os.killpg(proc.pid, signal.SIGINT)
        output, _ = proc.communicate(timeout=60)
    finally:
        _cleanup(proc, port)

    assert proc.returncode == 0, output
    assert "2 sessions were recorded; exported the newest" in output
    text = html.read_text()
    assert "reactive.calc doubled" in text and "output out" in text
    assert re.search(r'"source_file": "app.py"', text)
    assert re.search(r'"line": \d+', text)
    export = json.loads(out_json.read_text())
    assert any(e.get("label") == "input.n" for e in export["log"])
