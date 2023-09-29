"""Tools for parsing ipynb files."""
from __future__ import annotations

from pathlib import Path

__all__ = (
    "convert_ipynb_to_py",
    "get_shiny_deps",
)

from typing import TYPE_CHECKING, Literal, cast

from .._typing_extensions import NotRequired, TypedDict
from ..html_dependencies import jquery_deps, shiny_deps

# from htmltools import HTMLDependency


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


if TYPE_CHECKING:
    from htmltools._core import ScriptItem, StylesheetItem


def get_shiny_deps() -> str:
    import json

    deps = [
        jquery_deps().as_dict(lib_prefix=None, include_version=False),
        shiny_deps().as_dict(lib_prefix=None, include_version=False),
    ]

    # Convert from htmltools format to quarto format
    for dep in deps:
        if "script" in dep:
            dep["scripts"] = [htmltools_to_quarto_script(s) for s in dep.pop("script")]
        if "stylesheet" in dep:
            dep["stylesheets"] = [
                htmltools_to_quarto_stylesheet(s) for s in dep.pop("stylesheet")
            ]

        del dep["meta"]

    return json.dumps(deps, indent=2)


_shared_dir = (Path(__file__) / ".." / "..").resolve() / "www" / "shared"


def htmltools_to_quarto_script(dep: ScriptItem) -> QuartoHtmlDepItem:
    if dep["src"].startswith("shiny"):
        src = str(remove_first_dir(Path(dep["src"])))
    else:
        src = str(Path(dep["src"]))
    # NOTE: htmltools always prepends a directory after .as_dict() is called, so we'll
    # remove the first directory part.
    # src = str(remove_first_dir(Path(dep["src"])))

    return {
        "name": src,
        "path": str(_shared_dir / src),
    }


def htmltools_to_quarto_stylesheet(dep: StylesheetItem) -> QuartoHtmlDepItem:
    src = str(remove_first_dir(Path(dep["href"])))
    return {
        "name": src,
        "path": str(_shared_dir / src),
    }


def remove_first_dir(p: Path) -> Path:
    """Remove the first directory from a Path"""
    parts = p.parts

    # If there's only one part (just a filename), return it as is
    if len(parts) == 1:
        return p

    # Otherwise, skip the first directory and reconstruct the path
    return Path(parts[1]).joinpath(*parts[2:])
