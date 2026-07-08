from __future__ import annotations

import sys

import click

import shiny

from . import _static


@click.command(
    "static",
    help="""The functionality from `shiny static` has been moved to the shinylive package.
Please install shinylive and use `shinylive export` instead of `shiny static`:

  \b
  shiny static-assets remove
  pip install shinylive
  shinylive export APPDIR DESTDIR

""",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
def static() -> None:
    print(
        """The functionality from `shiny static` has been moved to the shinylive package.
Please install shinylive and use `shinylive export` instead of `shiny static`:

  shiny static-assets remove
  pip install shinylive
  shinylive export APPDIR DESTDIR
"""
    )
    sys.exit(1)


@click.command(
    "static-assets",
    no_args_is_help=True,
    help="""Manage local copy of assets for static app deployment. (Deprecated)

    \b
    Commands:
        remove: Remove local copies of assets.
        info: Print information about the local assets.

""",
)
@click.argument("command", type=str)
def static_assets(command: str) -> None:
    dir = _static.get_default_shinylive_dir()

    if command == "remove":
        print(f"Removing {dir}")
        _static.remove_shinylive_local(shinylive_dir=dir)
    elif command == "info":
        _static.print_shinylive_local_info()
    else:
        raise click.UsageError(f"Unknown command: {command}")


@click.command(
    "cells-to-app", help="""Convert a JSON file with code cells to a py file."""
)
@click.argument(
    "json_file",
    type=str,
)
@click.argument(
    "py_file",
    type=str,
)
def cells_to_app(json_file: str, py_file: str) -> None:
    shiny.quarto.convert_code_cells_to_app_py(json_file, py_file)


@click.command("get-shiny-deps", help="""Get Shiny's HTML dependencies as JSON.""")
def get_shiny_deps() -> None:
    print(shiny.quarto.get_shiny_deps())
