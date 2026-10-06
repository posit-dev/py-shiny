import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller

APP = Path(__file__).parent / "record_app" / "app.py"


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
    try:
        assert proc.stdout is not None
        first_line = proc.stdout.readline()
        url = re.search(r"http://\S+", first_line)
        assert url is not None, first_line

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
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()

    assert proc.returncode == 0, output
    assert "2 sessions were recorded; exported the newest" in output
    text = html.read_text()
    assert "reactive.calc doubled" in text and "output out" in text
    assert re.search(r'"source_file": "app.py"', text)
    assert re.search(r'"line": \d+', text)
    export = json.loads(out_json.read_text())
    assert any(e.get("label") == "input.n" for e in export["log"])
