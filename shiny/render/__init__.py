"""
Tools for reactively rendering output for the user interface.
"""


from . import (  # noqa: F401
    transformer,  # pyright: ignore[reportUnusedImport]
)

from ._deprecated import (  # noqa: F401
    RenderFunction,  # pyright: ignore[reportUnusedImport]
    RenderFunctionAsync,  # pyright: ignore[reportUnusedImport]
)

from ._render import (
    text,
    plot,
    image,
    table,
    ui,
)

from ._dataframe import (
    DataGrid,
    DataTable,
    data_frame,
)


__all__ = (
    # TODO-future: Document which variables are exposed via different import approaches
    "data_frame",
    "text",
    "plot",
    "image",
    "table",
    "ui",
    "DataGrid",
    "DataTable",
)
