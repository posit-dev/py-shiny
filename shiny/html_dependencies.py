from htmltools import HTMLDependency, HTML
from typing import List, Union


def shiny_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny",
        version="0.0.1",
        source={"package": "shiny", "subdir": "www/shared/"},
        script={"src": "shiny.js"},
        stylesheet={"href": "shiny.min.css"},
    )


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


def jquery_deps() -> HTMLDependency:
    return HTMLDependency(
        name="jquery",
        version="3.6.0",
        source={"package": "shiny", "subdir": "www/shared/jquery/"},
        script={"src": "jquery-3.6.0.min.js"},
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


import re
from ipywidgets._version import __html_manager_version__

html_manager_version = re.sub("^\\D*", "", __html_manager_version__)


def ipywidget_embed_deps() -> List[HTMLDependency]:
    return [
        HTMLDependency(
            name="requirejs",
            version="2.3.4",
            source={"package": "shiny", "subdir": "ipywidgets/lib"},
            script={"src": "require.min.js"},
        ),
        HTMLDependency(
            name="ipywidget-libembed-amd",
            version=html_manager_version,
            source={"package": "shiny", "subdir": "ipywidgets/lib"},
            script={"src": "libembed-amd.js"},
        ),
    ]


def ipywidget_output_dep() -> HTMLDependency:
    return HTMLDependency(
        name="ipywidget-output-binding",
        version="0.0.1",
        source={"package": "shiny", "subdir": "ipywidgets/dist"},
        script={"src": "output.js"},
    )


def ipywidget_input_dep() -> HTMLDependency:
    return HTMLDependency(
        name="ipywidget-input-binding",
        version="0.0.1",
        source={"package": "shiny", "subdir": "ipywidgets/dist"},
        script={"src": "input.js"},
    )
