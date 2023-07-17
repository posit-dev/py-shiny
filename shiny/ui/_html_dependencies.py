from __future__ import annotations

from htmltools import HTML, HTMLDependency

from .._versions import bootstrap as bootstrap_version
from .._versions import shiny_html_deps
from ..html_dependencies import jquery_deps
from ._x._htmldeps import nav_spacer_dependency


def nav_spacer_deps() -> list[HTMLDependency]:
    return [nav_spacer_dependency()]


def bootstrap_deps() -> list[HTMLDependency]:
    dep = HTMLDependency(
        name="bootstrap",
        version=bootstrap_version,
        source={"package": "shiny", "subdir": "www/shared/bootstrap/"},
        script={"src": "bootstrap.bundle.min.js"},
        stylesheet={"href": "bootstrap.min.css"},
        meta={"name": "viewport", "content": "width=device-width, initial-scale=1"},
    )
    deps = [jquery_deps(), dep]
    return deps


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
        # TODO: pre-compile the Bootstrap 5 version?
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
        # TODO: pre-compile the Bootstrap 5 version?
        stylesheet={"href": "css/selectize.bootstrap3.css"},
    )


def jqui_deps() -> HTMLDependency:
    return HTMLDependency(
        name="jquery-ui",
        version="1.12.1",
        source={"package": "shiny", "subdir": "www/shared/jqueryui/"},
        script={"src": "jquery-ui.min.js"},
        stylesheet={"href": "jquery-ui.min.css"},
    )
