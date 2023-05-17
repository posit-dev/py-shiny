from __future__ import annotations

__all__ = ("output_data_grid",)

from htmltools import HTMLDependency, Tag, div

from ..._namespaces import resolve_id

react_deps = HTMLDependency(
    "react",
    "18.2.0",
    source={
        "package": "shiny",
        "subdir": "ui/datagrid/js/dist/",
    },
    script=[{"src": "react.production.min.js"}],
)

react_dom_deps = HTMLDependency(
    "react-dom",
    "18.2.0",
    source={
        "package": "shiny",
        "subdir": "ui/datagrid/js/dist/",
    },
    script=[{"src": "react-dom.production.min.js"}],
)

glide_data_grid_deps = HTMLDependency(
    "shiny-glide-data-grid",
    "0.0.1",
    source={
        "package": "shiny",
        "subdir": "ui/datagrid/js/dist",
    },
    script=[{"src": "index.js"}],
    stylesheet=[{"href": "index.css"}],
)


def output_data_grid(id: str) -> Tag:
    return div(
        react_deps,
        react_dom_deps,
        glide_data_grid_deps,
        id=resolve_id(id),
        class_="shiny-glide-data-grid-output",
    )
