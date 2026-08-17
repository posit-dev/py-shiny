from __future__ import annotations

import click

from .. import __version__
from ._create import create
from ._docs import docs
from ._generate_test import add
from ._inspect import inspect
from ._mcp import mcp

# Re-exported as `shiny.run_app` (see `shiny/__init__.py`)
from ._run import run
from ._run import run_app as run_app  # noqa: F401
from ._scaffold import scaffold
from ._simulate import simulate
from ._skills import skills
from ._static import cells_to_app, get_shiny_deps, static, static_assets
from ._validate import validate


@click.group("main")
@click.version_option(__version__)
def main() -> None:
    pass


main.add_command(run)
main.add_command(add)
main.add_command(create)
main.add_command(validate)
main.add_command(simulate)
main.add_command(inspect)
main.add_command(docs)
main.add_command(scaffold)
main.add_command(mcp)
main.add_command(skills)
main.add_command(static)
main.add_command(static_assets)
main.add_command(cells_to_app)
main.add_command(get_shiny_deps)
