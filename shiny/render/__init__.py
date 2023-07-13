"""
Tools for reactively rendering output for the user interface.
"""

from ._render import (  # noqa: F401
    RenderFunctionMeta as RenderFunctionMeta,
    RenderFunction as RenderFunction,
    RenderFunctionAsync as RenderFunctionAsync,
    renderer_gen,
    text,
    plot,
    image,
    table,
    ui,
)

from ._dataframe import (  # noqa: F401
    DataGrid as DataGrid,
    DataTable as DataTable,
    data_frame,
)


__all__ = (
    # TODO-barret; Q: Remove `DataGrid` and `DataTable` methods from `__all__`
    # # Is `DataGrid` and `DataTable` necessary? I don't believe they are _render_ methods.
    # # They would be available via `from render import DataGrid`,
    # # just wouldn't be available as  `render.DataGrid`
    # "DataGrid",
    # "DataTable",
    # #
    "data_frame",
    "text",
    "plot",
    "image",
    "table",
    "ui",
    "renderer_gen",
)
