from __future__ import annotations

import click

from .. import __version__
from ._create import create
from ._generate_test import add

# Re-exported as `shiny.run_app` (see `shiny/__init__.py`)
from ._run import run
from ._run import run_app as run_app  # noqa: F401
from ._skills import skills
from ._static import cells_to_app, get_shiny_deps, static, static_assets


@click.group("main")
@click.version_option(__version__)
def main() -> None:
    pass


main.add_command(run)
main.add_command(add)
main.add_command(create)
main.add_command(skills)
main.add_command(static)
main.add_command(static_assets)
main.add_command(cells_to_app)
main.add_command(get_shiny_deps)
