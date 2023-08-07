"""
Tools for reactively rendering output for the user interface.
"""

from ._render import (  # noqa: F401
    # Values declared in `__all__` will give autocomplete hints / resolve.
    # E.g. `from shiny import render; render.text` but not `render.RenderMeta`
    # These values do not need ` as FOO` as the variable is used in `__all__`
    text,
    plot,
    image,
    table,
    ui,
    # Renamed values (in addition to the __all__values) are exposed when importing
    # directly from `render` module just like a regular variable.
    # E.g `from shiny.render import RenderMeta, RenderFnAsync, renderer_components`
    # These values need ` as FOO` as the variable is not used in `__all__` and causes an
    # reportUnusedImport error from pylance.
    # Using the same name is allowed.
    TransformerMetadata as TransformerMetadata,
    ValueFnAsync as ValueFnAsync,
    TransformerParams as TransformerParams,
    OutputTransformer as OutputTransformer,
    output_transformer as output_transformer,
    # Deprecated / legacy classes
    RenderFunction as RenderFunction,
    RenderFunctionAsync as RenderFunctionAsync,
)

from ._dataframe import (  # noqa: F401
    # Renamed values
    DataGrid as DataGrid,
    DataTable as DataTable,
    # Values declared in `__all__`
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
