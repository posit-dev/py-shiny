"""
Tools for reactively rendering output for the user interface.
"""

from . import (  # noqa: F401
    transformer,  # pyright: ignore[reportUnusedImport]
)
from ._data_frame import (
    CellPatch,
    CellValue,
    DataGrid,
    DataTable,
    data_frame,
)
from ._data_frame_utils._selection import CellSelection
from ._data_frame_utils._types import (  # noqa: F401
    StyleInfo,
)
from ._deprecated import (  # noqa: F401
    RenderFunction,  # pyright: ignore[reportUnusedImport]
    RenderFunctionAsync,  # pyright: ignore[reportUnusedImport]
)
from ._express import (
    express,
)
from ._render import (
    code,
    download,
    image,
    plot,
    table,
    text,
    ui,
)

__all__ = (
    # TODO-future: Document which variables are exposed via different import approaches
    "data_frame",
    "express",
    "text",
    "code",
    "plot",
    "image",
    "table",
    "ui",
    "download",
    "DataGrid",
    "DataTable",
    "CellPatch",
    "CellValue",
    "CellSelection",
    "StyleInfo",
)
