from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import click

from ..reactive._reactlog._record import (
    RecordingError,
    record_session,
    serve_and_collect,
)
from ..reactive._reactlog._viewer import (
    format_graph_mermaid,
    format_reactlog_html,
    load_reactlog_json,
)
from ._utils import cli_danger, cli_success


def _when(t: float | None) -> str:
    return "Active" if t is None else datetime.fromtimestamp(t).strftime("%H:%M:%S")


def _choose_interactively(sessions: list[dict[str, Any]]) -> list[str]:
    if len(sessions) == 1:
        return [sessions[0]["id"]]
    for i, s in enumerate(sessions, start=1):
        click.echo(
            f"  {i}. {s['id'][:12]}  started {_when(s['start'])}  ended {_when(s['end'])}"
        )
    pick = click.prompt("Session", type=click.IntRange(1, len(sessions)), default=1)
    return [sessions[pick - 1]["id"]]


def _wait_for_enter() -> None:
    click.prompt("", default="", show_default=False, prompt_suffix="")


def _with_suffix(path: Path, suffix: str | None) -> Path:
    return (
        path if suffix is None else path.with_name(f"{path.stem}-{suffix}{path.suffix}")
    )


@click.command(
    "reactlog",
    help="""Record a Shiny app's real reactive activity and export it as a Reactlog.

    Runs the app with reactlog enabled and opens a browser (recorded to video). Interact
    with the app, then press Enter or close the window. Use --no-browser to drive the app
    yourself (or with another tool), or pass a saved .json reactlog to view it again.

    Examples:

        shiny reactlog app.py
        shiny reactlog app.py --html report.html --json report.json
        shiny reactlog app.py --no-browser --all
        shiny reactlog report.json --html
    """,
)
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option("--code", type=str, default=None, help="Inline app source code to run.")
@click.option(
    "--html",
    "html_out",
    type=str,
    is_flag=False,
    flag_value="reactlog.html",
    default=None,
    help="Write the interactive HTML viewer (default when no output is given: reactlog.html).",
)
@click.option(
    "--json",
    "json_out",
    type=str,
    default=None,
    help="Write the recorded reactlog as JSON.",
)
@click.option(
    "--mermaid",
    "mermaid_out",
    type=str,
    default=None,
    help="Write the recorded graph as Mermaid.",
)
@click.option(
    "--video",
    "video_out",
    type=str,
    default=None,
    help="Where to save the browser video (default: next to the HTML file).",
)
@click.option(
    "--no-browser",
    is_flag=True,
    default=False,
    help="Don't open a browser; print the app URL and wait for Enter.",
)
@click.option(
    "--all",
    "all_sessions",
    is_flag=True,
    default=False,
    help="With --no-browser, export every recorded session.",
)
@click.option(
    "--redact-inputs", is_flag=True, default=False, help="Redact all input values."
)
@click.option("--title", type=str, default=None, help="Title for the HTML viewer.")
@click.option(
    "--theme",
    type=click.Choice(["dark", "light", "auto"], case_sensitive=False),
    default="dark",
    help="Theme for the HTML viewer.",
)
def reactlog(
    path: str | None,
    code: str | None,
    html_out: str | None,
    json_out: str | None,
    mermaid_out: str | None,
    video_out: str | None,
    no_browser: bool,
    all_sessions: bool,
    redact_inputs: bool,
    title: str | None,
    theme: str,
) -> None:
    # `--html` takes an optional value, so `shiny reactlog --html app.py` makes
    # `app.py` the output path. Treat an app/JSON/dir value as the input instead.
    if (
        path is None
        and html_out is not None
        and (
            Path(html_out).suffix.lower() in (".py", ".json") or Path(html_out).is_dir()
        )
    ):
        path, html_out = html_out, "reactlog.html"
    if html_out is None and json_out is None and mermaid_out is None:
        html_out = "reactlog.html"

    try:
        with tempfile.TemporaryDirectory() as tmp:
            input_file = _resolve_input(path, code=code, tmp_dir=Path(tmp))
            outputs = [
                Path(p) for p in (html_out, json_out, mermaid_out) if p is not None
            ]
            for out in outputs:
                if out.resolve() == input_file.resolve():
                    raise RecordingError(
                        f"Refusing to overwrite the input file {input_file}."
                    )

            video_path: Path | None = None
            if input_file.suffix.lower() == ".json":
                exports = [json.loads(input_file.read_text(encoding="utf-8"))]
            elif no_browser:
                exports = serve_and_collect(
                    input_file,
                    on_ready=lambda url: click.echo(
                        f"App running at {url}\nInteract with it, then press Enter to export."
                    ),
                    wait=_wait_for_enter,
                    choose=(
                        (lambda ss: [s["id"] for s in ss])
                        if all_sessions
                        else _choose_interactively
                    ),
                )
            else:
                if video_out is not None:
                    video_path = Path(video_out)
                elif html_out is not None:
                    video_path = Path(html_out).with_suffix(".webm")
                rec = record_session(
                    input_file, video_path=video_path, redact_inputs=redact_inputs
                )
                exports = [rec.export]
                video_path = rec.video_path

            for export in exports:
                suffix = (
                    str(export.get("session", ""))[:8] if len(exports) > 1 else None
                )
                _write_outputs(
                    export,
                    html_out=_with_suffix(Path(html_out), suffix) if html_out else None,
                    json_out=_with_suffix(Path(json_out), suffix) if json_out else None,
                    mermaid_out=(
                        _with_suffix(Path(mermaid_out), suffix) if mermaid_out else None
                    ),
                    video_path=video_path,
                    title=title,
                    theme=theme,
                )
    except RecordingError as err:
        click.echo(cli_danger(str(err)))
        sys.exit(1)


def _resolve_input(path: str | None, *, code: str | None, tmp_dir: Path) -> Path:
    if code is not None or path == "-":
        source = code if code is not None else sys.stdin.read()
        app = tmp_dir / "app.py"
        app.write_text(source, encoding="utf-8")
        return app
    p = Path(path or "app.py")
    if p.is_dir():
        p = p / "app.py"
    if not p.is_file():
        raise RecordingError(f"File not found: {p}")
    return p


def _write_outputs(
    export: dict[str, Any],
    *,
    html_out: Path | None,
    json_out: Path | None,
    mermaid_out: Path | None,
    video_path: Path | None,
    title: str | None,
    theme: str,
) -> None:
    data = load_reactlog_json(export)
    if html_out is not None:
        entry = str(export.get("entry_file") or "")
        html = format_reactlog_html(
            data,
            str(export.get("sources", {}).get(entry, "")),
            title=title or entry or "Shiny App",
            video_path=str(video_path) if video_path is not None else None,
            html_path=str(html_out),
            theme=theme,
        )
        html_out.write_text(html, encoding="utf-8")
        click.echo(cli_success(f"Reactlog viewer written to {html_out}"))
    if json_out is not None:
        json_out.write_text(json.dumps(export, indent=2), encoding="utf-8")
        click.echo(cli_success(f"Reactlog JSON written to {json_out}"))
    if mermaid_out is not None:
        mermaid_out.write_text(format_graph_mermaid(data), encoding="utf-8")
        click.echo(cli_success(f"Mermaid graph written to {mermaid_out}"))
