from __future__ import annotations

__all__ = ("output_data_frame",)

from htmltools import Tag

from ..._namespaces import resolve_id
from .._html_deps_py_shiny import data_frame_deps
from ..fill import as_fill_item, as_fillable_container


def output_data_frame(id: str) -> Tag:
    """
    Create an output container for an interactive table or grid. Features fast
    virtualized scrolling, sorting, filtering, and row selection (single or multiple).

    Parameters
    ----------
    id
        An output id.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    :func:`~shiny.render.data_frame`
    """
    return as_fillable_container(
        as_fill_item(
            Tag(
                "shiny-data-frame",
                data_frame_deps(),
                id=resolve_id(id),
            ),
        )
    )
