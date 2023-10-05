"""Tools for parsing ipynb files."""
from __future__ import annotations

from pathlib import Path

__all__ = (
    "convert_code_cells_to_app_py",
    "get_shiny_deps",
)

from typing import Literal, cast

from .._typing_extensions import NotRequired, TypedDict

QuartoShinyCodeCellClass = Literal["python", "r", "cell-code", "hidden"]


class QuartoShinyCodeCell(TypedDict):
    text: str
    classes: list[QuartoShinyCodeCellClass]


class QuartoShinyCodeCells(TypedDict):
    schema_version: int
    cells: list[QuartoShinyCodeCell]


def convert_code_cells_to_app_py(file: str | Path) -> None:
    """Parse an code cell JSON file and output an app.py file."""
    import json

    file = Path(file)

    with open(file, "r") as f:
        data = cast(QuartoShinyCodeCells, json.load(f))

    if data["schema_version"] != 1:
        raise ValueError("Only schema_version 1 is supported.")

    cells = data["cells"]

    code_cell_texts: list[str] = []

    for cell in cells:
        if "python" not in cell["classes"]:
            continue

        if cell["text"].startswith("#| skip: true"):
            continue

        code_cell_texts.append(
            "    "
            + "    ".join(cell["text"])
            + "\n\n    # ============================\n"
        )

    app_content = f"""
from pathlib import Path
from shiny import App, Inputs, Outputs, Session, ui

def server(input: Inputs, output: Outputs, session: Session) -> None:
{ "".join(code_cell_texts) }

app = App(
    Path(__file__).parent / "{ file.with_suffix(".html").name }",
    server,
    static_assets=Path(__file__).parent,
)
    """

    # print(app_content)

    with open("app.py", "w") as f:
        f.write(app_content)


# =============================================================================
# HTML Dependency types
# =============================================================================
class QuartoHtmlDepItem(TypedDict):
    name: str
    path: str
    attribs: NotRequired[dict[str, str]]


class QuartoHtmlDepServiceworkerItem(TypedDict):
    source: str
    destination: str


class QuartoHtmlDependency(TypedDict):
    name: str
    version: NotRequired[str]
    scripts: NotRequired[list[str | QuartoHtmlDepItem]]
    stylesheets: NotRequired[list[str | QuartoHtmlDepItem]]
    resources: NotRequired[list[QuartoHtmlDepItem]]
    meta: NotRequired[dict[str, str]]
    serviceworkers: NotRequired[list[QuartoHtmlDepServiceworkerItem]]


def placeholder_dep() -> QuartoHtmlDependency:
    return {
        "name": "shiny-dependency-placeholder",
        "version": "9.9.9",
        "meta": {"shiny-dependency-placeholder": ""},
    }


def get_shiny_deps() -> str:
    import json

    return json.dumps([placeholder_dep()], indent=2)
