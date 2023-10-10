from __future__ import annotations

__all__ = ("output_data_frame",)

from htmltools import HTMLDependency, Tag

from ... import __version__
from ..._namespaces import resolve_id
from ..fill import as_fill_carrier


def data_frame_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-data-frame-output",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "www/shared/dataframe",
        },
        script={"src": "dataframe.js", "type": "module"},
    )


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
    return as_fill_carrier(
        Tag(
            "shiny-data-frame",
            data_frame_deps(),
            id=resolve_id(id),
        ),
    )
