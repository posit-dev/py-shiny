from __future__ import annotations

import click

QUICKSTART_TEXT = """\
# Shiny for Python Quickstart

Build reactive web applications in pure Python.

## Quick Example (`app.py`)
```python
from shiny.express import input, render, ui

ui.input_slider("n", "N", 0, 100, 20)

@render.text
def txt():
    return f"Value squared: {input.n() ** 2}"
```

## Run the App
```bash
shiny run --reload app.py          # Start dev server with live reload
```

## On-Demand Documentation (CLI)
Query targeted docs directly to stdout (zero-install progressive disclosure):
```bash
shiny docs                        # List all 27 available doc topics
shiny docs reactivity             # Core reactive graph & primitives
shiny docs express                # Express mode & layout
shiny docs layouts                # Cards, sidebars, grids, value boxes
shiny docs test-server            # Fast in-memory unit testing
```

## Coding Agent Skills (Optional)
Link bundled Agent Skills into your workspace for persistent agent integration:
```bash
uvx library-skills --claude       # Claude Code (.claude/skills)
uvx library-skills                # Other agents (.agents/skills)
```

## Resources & Key Features
- Docs: https://shiny.posit.co/py/ | Templates: `shiny create`
- Features: Chat (`ui.Chat`), Markdown streaming, OTel tracing, DataGrid, brand.yml
"""


@click.command(
    "quickstart",
    help="Print a concise quickstart guide and agent cheat sheet to stdout.",
)
def quickstart() -> None:
    click.echo(QUICKSTART_TEXT, nl=False)
