__all__ = ()

from typing import List, Union

from htmltools import HTML, HTMLDependency

from ..html_dependencies import jquery_deps


def bootstrap_deps(bs3compat: bool = True) -> List[HTMLDependency]:
    dep = HTMLDependency(
        name="bootstrap",
        version="5.0.1",
        source={"package": "shiny", "subdir": "www/shared/bootstrap/"},
        script={"src": "bootstrap.bundle.min.js"},
        stylesheet={"href": "bootstrap.min.css"},
    )
    deps = [jquery_deps(), dep]
    if bs3compat:
        deps.append(bs3compat_deps())
    return deps


# TODO: if we want to support glyphicons we'll need to bundle font files, too
def bs3compat_deps() -> HTMLDependency:
    return HTMLDependency(
        name="bs3-compat",
        version="1.0",
        source={"package": "shiny", "subdir": "www/shared/bs3compat/"},
        script=[{"src": "transition.js"}, {"src": "tabs.js"}, {"src": "bs3compat.js"}],
    )


def nav_deps(
    include_bootstrap: bool = True,
) -> Union[HTMLDependency, List[HTMLDependency]]:
    dep = HTMLDependency(
        name="bslib-navs",
        version="1.0",
        source={"package": "shiny", "subdir": "www/shared/bslib/dist/"},
        script={"src": "navs.min.js"},
    )
    return [dep, *bootstrap_deps()] if include_bootstrap else dep


def ionrangeslider_deps() -> List[HTMLDependency]:
    return [
        HTMLDependency(
            name="ionrangeslider",
            version="2.3.1",
            source={"package": "shiny", "subdir": "www/shared/ionrangeslider/"},
            script={"src": "js/ion.rangeSlider.min.js"},
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
