"""Tools for parsing ipynb files."""
from __future__ import annotations

from pathlib import Path

__all__ = (
    "convert_ipynb_to_py",
    "get_shiny_deps",
)

from typing import Literal, cast

from .._typing_extensions import NotRequired, TypedDict


class NbCellCodeOutputStream(TypedDict):
    output_type: Literal["stream"]
    name: Literal["stdout", "stderr"]
    text: list[str]


class NbCellCodeOutputDisplayData(TypedDict):
    output_type: Literal["display_data"]
    metadata: dict[str, object]
    data: dict[str, object]


class NbCellCodeOutputExecuteResult(TypedDict):
    output_type: Literal["execute_result"]
    execution_count: int
    metadata: dict[str, object]
    data: dict[str, object]


NbCellCodeOutput = (
    NbCellCodeOutputStream | NbCellCodeOutputDisplayData | NbCellCodeOutputExecuteResult
)


class NbCellCode(TypedDict):
    cell_type: Literal["code"]
    execution_count: int | None
    id: str
    metadata: dict[str, object]
    source: str | list[str]
    outputs: list[NbCellCodeOutput]


class NbCellMarkdown(TypedDict):
    cell_type: Literal["markdown"]
    metadata: dict[str, object]
    source: str | list[str]


class NbCellRaw(TypedDict):
    cell_type: Literal["raw"]
    metadata: dict[str, object]
    source: str | list[str]


NbCell = NbCellCode | NbCellMarkdown | NbCellRaw


class Ipynb(TypedDict):
    cells: list[NbCell]
    metadata: dict[str, object]
    nbformat: int
    nbformat_minor: int


def convert_ipynb_to_py(file: str | Path) -> None:
    """Parse an ipynb file."""
    import json

    file = Path(file)

    with open(file, "r") as f:
        nb = cast(Ipynb, json.load(f))

    cells = nb["cells"]

    code_cell_sources: list[str] = []

    for cell in cells:
        if cell["cell_type"] != "code":
            continue

        if "skip" in cell["metadata"] and cell["metadata"]["skip"] is True:
            continue

        code_cell_sources.append(
            "    "
            + "    ".join(cell["source"])
            + "\n\n    # ============================\n"
        )

    app_content = f"""
from pathlib import Path
from shiny import App, Inputs, Outputs, Session, ui

def server(input: Inputs, output: Outputs, session: Session) -> None:
{ "".join(code_cell_sources) }

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
