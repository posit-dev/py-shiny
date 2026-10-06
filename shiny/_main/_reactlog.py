from __future__ import annotations

import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import click

from ..reactive._reactlog._record import (
    RecordingError,
    record_session,
    redact_export,
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


def _is_interactive() -> bool:
    return sys.stdin is not None and sys.stdin.isatty()


def _wait_for_enter() -> None:
    """Block until the user finishes: Enter on a terminal, else Ctrl+C / SIGINT."""
    try:
        if _is_interactive():
            click.prompt("", default="", show_default=False, prompt_suffix="")
        else:
            # Piped or closed stdin would hit EOF at once, so wait for a signal.
            while True:
                time.sleep(0.5)
    except (click.Abort, EOFError, KeyboardInterrupt):
        pass


def _load_saved(path: Path) -> dict[str, Any]:
    try:
        export = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:  # JSONDecodeError and UnicodeDecodeError
        raise RecordingError(f"Not a reactlog JSON file: {path}") from err
    if not isinstance(export, dict):
        raise RecordingError(f"Not a reactlog JSON file: {path}")
    export = cast("dict[str, Any]", export)
    if not isinstance(export.get("log"), list):
        raise RecordingError(f"Not a reactlog JSON file: {path}")
    return export


def _check_paths(input_file: Path, outputs: list[Path]) -> None:
    seen: set[Path] = set()
    for out in outputs:
        resolved = out.resolve()
        if resolved == input_file.resolve():
            raise RecordingError(f"Refusing to overwrite the input file {input_file}.")
        if resolved in seen:
            raise RecordingError(f"{out} is used for more than one output.")
        seen.add(resolved)


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
            saved_input = input_file.suffix.lower() == ".json"
            if no_browser and video_out is not None:
                raise click.UsageError("--video cannot be used with --no-browser.")
            if all_sessions and not no_browser:
                raise click.UsageError("--all requires --no-browser.")
            if saved_input and (no_browser or video_out is not None or all_sessions):
                raise click.UsageError(
                    "--no-browser, --video, and --all do not apply to a saved .json reactlog."
                )

            video_path: Path | None = None
            if not (saved_input or no_browser):
                if video_out is not None:
                    video_path = Path(video_out)
                elif html_out is not None:
                    video_path = Path(html_out).with_suffix(".webm")
            out_paths = [
                Path(p) for p in (html_out, json_out, mermaid_out) if p is not None
            ]
            # Fail before recording, not after.
            _check_paths(
                input_file,
                out_paths + ([video_path] if video_path is not None else []),
            )

            if saved_input:
                exports = [_load_saved(input_file)]
            elif no_browser:
                finish = "press Enter" if _is_interactive() else "press Ctrl+C"
                exports = serve_and_collect(
                    input_file,
                    on_ready=lambda url: click.echo(
                        f"App running at {url}\nInteract with it, then {finish} to export."
                    ),
                    wait=_wait_for_enter,
                    choose=(
                        (lambda ss: [s["id"] for s in ss])
                        if all_sessions
                        else _choose_interactively
                    ),
                )
            else:
                rec = record_session(
                    input_file, video_path=video_path, redact_inputs=redact_inputs
                )
                exports = [rec.export]
                video_path = rec.video_path

            if redact_inputs:
                for export in exports:
                    redact_export(export)

            targets = [
                (
                    export,
                    _with_suffix(Path(html_out), suffix) if html_out else None,
                    _with_suffix(Path(json_out), suffix) if json_out else None,
                    _with_suffix(Path(mermaid_out), suffix) if mermaid_out else None,
                )
                for export in exports
                for suffix in [
                    str(export.get("session", ""))[:8] if len(exports) > 1 else None
                ]
            ]
            _check_paths(
                input_file,
                [p for _, *ps in targets for p in ps if p is not None]
                + ([video_path] if video_path is not None else []),
            )
            for export, html_p, json_p, mermaid_p in targets:
                _write_outputs(
                    export,
                    html_out=html_p,
                    json_out=json_p,
                    mermaid_out=mermaid_p,
                    video_path=video_path,
                    title=title,
                    theme=theme,
                )
            if video_path is not None:
                click.echo(cli_success(f"Video saved to {video_path}"))
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


def _write(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as err:
        raise RecordingError(f"Could not write {path}: {err}") from err


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
        _write(html_out, html)
        click.echo(cli_success(f"Reactlog viewer written to {html_out}"))
    if json_out is not None:
        _write(json_out, json.dumps(export, indent=2))
        click.echo(cli_success(f"Reactlog JSON written to {json_out}"))
    if mermaid_out is not None:
        _write(mermaid_out, format_graph_mermaid(data))
        click.echo(cli_success(f"Mermaid graph written to {mermaid_out}"))
