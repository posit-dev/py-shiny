from __future__ import annotations

from typing import Literal

from htmltools import HTML, HTMLDependency

from .._versions import bootstrap as bootstrap_version
from .._versions import shiny_html_deps
from ..html_dependencies import jquery_deps

"""
HTML dependencies for external dependencies Bootstrap, ionrangeslider, datepicker, selectize, and jQuery UI.

For...
* External dependencies (e.g. jQuery, Bootstrap), see `shiny.ui._html_deps_external`
* Internal dependencies (e.g. dataframe, autoresize), see `shiny.ui._html_deps_py_shiny`
* shinyverse dependencies (e.g. bslib, htmltools), see `shiny.ui._html_deps_shinyverse`
"""


def bootstrap_deps() -> list[HTMLDependency]:
    bootstrap_css = HTMLDependency(
        name="bootstrap-css",
        version=bootstrap_version,
        source={"package": "shiny", "subdir": "www/shared/bootstrap/"},
        stylesheet={"href": "bootstrap.min.css"},
    )

    bootstrap_js = HTMLDependency(
        name="bootstrap-js",
        version=bootstrap_version,
        source={"package": "shiny", "subdir": "www/shared/bootstrap/"},
        script={"src": "bootstrap.bundle.min.js"},
    )

    bootstrap_meta = HTMLDependency(
        name="bootstrap-meta",
        version=bootstrap_version,
        source={"package": "shiny", "subdir": "www/shared/bootstrap/"},
        meta={"name": "viewport", "content": "width=device-width, initial-scale=1"},
    )

    return [
        jquery_deps(),
        bootstrap_meta,
        bootstrap_js,
        bootstrap_css,
    ]


def bootstrap_deps_suppress(
    parts: list[Literal["css", "js", "meta"]]
) -> list[HTMLDependency]:
    bs_v_suppressed = str(bootstrap_version) + ".9999"

    return [
        HTMLDependency(name=f"bootstrap-{part}", version=bs_v_suppressed)
        for part in parts
    ]


def ionrangeslider_deps() -> list[HTMLDependency]:
    return [
        HTMLDependency(
            name="ionrangeslider",
            version="2.3.1",
            source={"package": "shiny", "subdir": "www/shared/ionrangeslider/"},
            script={"src": "js/ion.rangeSlider.min.js"},
        ),
        HTMLDependency(
            name="preset-shiny-ionrangeslider",
            version=shiny_html_deps,
            source={"package": "shiny", "subdir": "www/shared/ionrangeslider/"},
            stylesheet={"href": "css/ion.rangeSlider.css"},
        ),
        HTMLDependency(
            name="strftime",
            version="0.9.2",
            source={"package": "shiny", "subdir": "www/shared/strftime/"},
            script={"src": "strftime-min.js"},
        ),
    ]


def datepicker_deps() -> HTMLDependency:
    return HTMLDependency(
        name="bootstrap-datepicker",
        version="1.9.0",
        source={"package": "shiny", "subdir": "www/shared/datepicker/"},
        stylesheet={"href": "css/bootstrap-datepicker3.min.css"},
        script={"src": "js/bootstrap-datepicker.min.js"},
        # Need to enable noConflict mode. See #1346.
        head=HTML(
            "<script>(function() { var datepicker = $.fn.datepicker.noConflict(); $.fn.bsDatepicker = datepicker; })();</script>"
        ),
    )


def selectize_deps() -> HTMLDependency:
    return HTMLDependency(
        name="selectize",
        version="0.12.6",
        source={"package": "shiny", "subdir": "www/shared/selectize/"},
        script=[
            {"src": "js/selectize.min.js"},
            {"src": "accessibility/js/selectize-plugin-a11y.min.js"},
        ],
        stylesheet={"href": "css/selectize.min.css"},
    )


def jqui_deps() -> HTMLDependency:
    return HTMLDependency(
        name="jquery-ui",
        version="1.12.1",
        source={"package": "shiny", "subdir": "www/shared/jqueryui/"},
        script={"src": "jquery-ui.min.js"},
        stylesheet={"href": "jquery-ui.min.css"},
    )
