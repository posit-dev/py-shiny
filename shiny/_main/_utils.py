from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from typing import Optional

import click
import questionary


def directory_prompt(
    dest_dir: Optional[Path | str | None] = None,
    default_dir: Optional[str | None] = None,
) -> Path:
    if dest_dir is not None:
        dest_dir = Path(dest_dir)

        if dest_dir.exists() and dest_dir.is_file():
            click.echo(
                cli_danger(
                    f"Error: Destination directory {cli_field(str(dest_dir))} is a file, not a directory."
                )
            )
            sys.exit(1)
        return dest_dir

    app_dir = questionary.path(
        "Enter destination directory:",
        default=path_rel_wd(default_dir) if default_dir is not None else "./",
        only_directories=True,
    ).ask()

    if app_dir is None:
        sys.exit(1)

    # Perform not-a-file check on the selected `app_dir`
    return directory_prompt(dest_dir=app_dir)


def path_rel_wd(*path: str):
    """
    Path relative to the working directory, formatted for the current OS
    """
    return os.path.join(".", *(path or [""]))


# CLI Style Helpers -----------------------------------------------------------------


def cli_field(x: str):
    return click.style(x, fg="cyan")


def cli_bold(x: str):
    return click.style(x, bold=True)


def cli_ital(x: str):
    return click.style(x, italic=True)


def cli_input(x: str):
    return click.style(x, fg="green")


def cli_code(x: str):
    return click.style("`" + x + "`", fg="magenta")


def cli_verbatim(x: str | list[str], indent: int = 2):
    lines = [click.style(line, fg="cyan") for line in x if line != ""]
    return textwrap.indent("\n".join(lines), " " * indent)


def cli_url(x: str):
    return click.style(x, fg="blue", underline=True)


def cli_success(x: str):
    return click.style("\u2713", fg="green") + " " + x


def cli_info(x: str):
    return click.style("\u2139", fg="blue") + " " + x


def cli_action(x: str):
    return click.style("→", fg="blue") + " " + x


def cli_warning(x: str):
    return click.style("!", fg="yellow") + " " + x


def cli_danger(x: str):
    return click.style("\u00d7", fg="red") + " " + x


def cli_wait(x: str):
    return click.style("\u2026", fg="yellow") + " " + x
