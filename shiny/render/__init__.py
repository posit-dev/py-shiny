"""
Tools for reactively rendering output for the user interface.
"""

from ._render import (  # noqa: F401
    # Exported. Give autocomplete hints for `shiny.render.FOO`
    text,
    plot,
    image,
    table,
    ui,
    # Manual imports. Do not give autocomplete hints.
    RenderMeta as RenderMeta,
    RenderFnAsync as RenderFnAsync,
    RendererParams as RendererParams,
    RendererComponents as RendererComponents,
    renderer_components as renderer_components,
    # Deprecated / legacy classes
    RenderFunction as RenderFunction,
    RenderFunctionAsync as RenderFunctionAsync,
)

from ._dataframe import (  # noqa: F401
    # Manual imports
    DataGrid as DataGrid,
    DataTable as DataTable,
    # Exported
    data_frame,
)


__all__ = (
    "data_frame",
    "text",
    "plot",
    "image",
    "table",
    "ui",
)
