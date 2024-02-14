"""
Tools for reactively rendering output for the user interface.
"""

from . import (  # noqa: F401
    transformer,  # pyright: ignore[reportUnusedImport]
)
from ._dataframe import (
    DataGrid,
    DataTable,
    data_frame,
)
from ._express import (
    express,
)
from ._render import (
    code,
    image,
    plot,
    table,
    text,
    ui,
    download,
)
from ._deprecated import (  # noqa: F401
    RenderFunction,  # pyright: ignore[reportUnusedImport]
    RenderFunctionAsync,  # pyright: ignore[reportUnusedImport]
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
)
