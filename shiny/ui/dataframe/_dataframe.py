from __future__ import annotations

__all__ = ("output_data_frame",)

from htmltools import HTMLDependency, Tag

from ... import __version__
from ..._namespaces import resolve_id


def data_frame_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-data-frame-output",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "ui/dataframe/js/dist",
        },
        script=[
            {"src": "index.js", "type": "module"},
        ],
    )


def output_data_frame(id: str) -> Tag:
    return Tag(
        "shiny-data-frame",
        data_frame_deps(),
        id=resolve_id(id),
    )
