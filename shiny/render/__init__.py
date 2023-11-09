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
from ._deprecated import (  # noqa: F401
    RenderFunction,  # pyright: ignore[reportUnusedImport]
    RenderFunctionAsync,  # pyright: ignore[reportUnusedImport]
)
from ._display import (
    display,
)
from ._render import (
    image,
    plot,
    table,
    text,
    ui,
)

__all__ = (
    # TODO-future: Document which variables are exposed via different import approaches
    "data_frame",
    "display",
    "text",
    "plot",
    "image",
    "table",
    "ui",
    "DataGrid",
    "DataTable",
)
