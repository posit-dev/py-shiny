from __future__ import annotations

__all__ = ("output_data_frame",)

from htmltools import HTMLDependency, Tag

from ... import __version__
from ..._namespaces import resolve_id
from ...experimental.ui._fill import bind_fill_role


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
    Create a output container for a data frame.

    Parameters
    ----------
    id
        An input id.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    :func:`~shiny.render.data_frame`
    """
    return bind_fill_role(
        Tag(
            "shiny-data-frame",
            data_frame_deps(),
            id=resolve_id(id),
        ),
        item=True,
        container=True,
    )
