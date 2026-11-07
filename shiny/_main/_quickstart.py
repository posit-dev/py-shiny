from __future__ import annotations

import click
from packaging.version import Version

from .. import __version__


@click.command(
    "quickstart",
    help="""Print a short welcome with setup steps, agent skills, and docs links.

    Run with `uvx shiny quickstart`, or `uv run shiny quickstart` to use your
    project's installed version of Shiny.
    """,
)
def quickstart() -> None:
    ref = "main" if Version(__version__).is_devrelease else f"v{__version__}"
    click.echo(
        f"""# Welcome to Shiny for Python {__version__}

Build reactive web apps in Python.

## Start a project
```sh
uv init myapp
cd myapp
uv add shiny
uv run shiny create
uv run shiny run app.py --reload --launch-browser
```

## Optional: help your coding agent
In this project, run `uvx library-skills` (Claude Code: add `--claude`).
Locate the bundled skill: `uv run shiny skills path shiny-for-python`.
Read `SKILL.md` there, or browse topics with `uv run shiny guide`.

## What's new and docs
[What's new in {__version__}](https://github.com/posit-dev/py-shiny/blob/{ref}/CHANGELOG.md)
[Get started](https://shiny.posit.co/py/get-started/) | [Docs](https://shiny.posit.co/py/docs/overview.html)
""",
        nl=False,
    )
