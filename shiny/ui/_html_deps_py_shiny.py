from __future__ import annotations

from htmltools import HTMLDependency

from .. import __version__


def data_frame_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-data-frame-output",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "www/shared/py-shiny/dataframe",
        },
        script={"src": "dataframe.js", "type": "module"},
    )


def autoresize_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-textarea-autoresize",
        __version__,
        source={"package": "shiny", "subdir": "www/shared/py-shiny/text-area"},
        script={"src": "textarea-autoresize.js"},
        stylesheet={"href": "textarea-autoresize.css"},
    )
