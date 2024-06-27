from __future__ import annotations

import os

from htmltools import HTMLDependency

from . import __version__
from .ui._html_deps_py_shiny import busy_indicators_dep


def shiny_deps(include_css: bool = True) -> list[HTMLDependency]:
    deps = [
        HTMLDependency(
            name="shiny",
            version=__version__,
            source={"package": "shiny", "subdir": "www/shared/"},
            script={"src": "shiny.js"},
            # This CSS is now rendered against default Bootstrap
            stylesheet={"href": "shiny.min.css"} if include_css else None,
        ),
        busy_indicators_dep(),
    ]

    if os.getenv("SHINY_DEV_MODE") == "1":
        deps.append(
            HTMLDependency(
                "shiny-devmode",
                version=__version__,
                head="<script>window.__SHINY_DEV_MODE__ = true;</script>",
            )
        )

    return deps


def jquery_deps() -> HTMLDependency:
    return HTMLDependency(
        name="jquery",
        version="3.6.0",
        source={"package": "shiny", "subdir": "www/shared/jquery/"},
        script={"src": "jquery-3.6.0.min.js"},
    )


# Shiny doesn't (currently) use requirejs directly, but it does include it because a
# custom requirejs setup is need to get HTMLDependency()s (i.e., loading JS via <script>
# tags) to be usable. At the moment, we're just setting `window.define.amd=false` after
# loading requirejs so that the typical UMD pattern won't result in an anonymous
# define() error.
# https://requirejs.org/docs/errors.html#mismatch
# https://github.com/umdjs/umd
#
# Someday, we may want the same/similar thing in R, but this definitely more of an
# immediate issue for Python since many Jupyter extensions use requirejs.
def require_deps() -> HTMLDependency:
    return HTMLDependency(
        name="requirejs",
        version="2.3.6",
        source={"package": "shiny", "subdir": "www/shared/requirejs/"},
        script={"src": "require.min.js"},
    )
