from typing import List
from htmltools import html_dependency

def shiny_deps() -> html_dependency:
  return html_dependency(
    name = "shiny",
    version = "0.0.1",
    package = "shiny",
    src = "www/shared",
    script = "shiny.js",
    stylesheet = "shiny.min.css"
  )

def bootstrap_deps(bs3compat = True) -> html_dependency:
  dep = html_dependency(
    name = "bootstrap",
    version = "5.0.1",
    src = "www/shared/bootstrap",
    package = "shiny",
    script = "bootstrap.bundle.min.js",
    stylesheet = "bootstrap.min.css"
  )
  deps = [jquery_deps(), dep]
  if bs3compat:
    deps.append(bs3compat_deps())
  return deps

# TODO: if we want to support glyphicons we'll need to bundle font files, too
def bs3compat_deps() -> html_dependency:
  return html_dependency(
    name="bs3-compat",
    version="1.0",
    src="www/shared/bs3compat",
    package="shiny",
    script=["transition.js", "tabs.js", "bs3compat.js"]
  )

def jquery_deps() -> html_dependency:
  return html_dependency(
    name = "jquery",
    version = "3.6.0",
    package = "shiny",
    src = "www/shared/jquery",
    script = "jquery-3.6.0.min.js",
  )


def nav_deps(include_bootstrap = True) -> html_dependency:
  dep = html_dependency(
    name = "bslib-navs",
    version = "1.0",
    package = "shiny",
    src = "www/shared/bslib/dist",
    script = "navs.min.js"
  )
  return [dep, bootstrap_deps()] if include_bootstrap else dep


def ionrangeslider_deps() -> List[html_dependency]:
  return [
    html_dependency(
      name = "ionrangeslider",
      version = "2.3.1",
      package = "shiny",
      src = "www/shared/ionrangeslider",
      script = "js/ion.rangeSlider.min.js",
      stylesheet = "css/ion.rangeSlider.css",
    ),
    html_dependency(
      name = "strftime",
      version = "0.9.2",
      package = "shiny",
      src = "www/shared/strftime",
      script = "strftime-min.js"
    )
  ]


def datepicker_deps() -> html_dependency:
  return html_dependency(
    name = "bootstrap-datepicker",
    version = "1.9.0",
    package = "shiny",
    src = "www/shared/datepicker",
    # TODO: pre-compile the Bootstrap 5 version?
    stylesheet = "css/bootstrap-datepicker3.min.css",
    script = "js/bootstrap-datepicker.min.js",
    # Need to enable noConflict mode. See #1346.
    head = "<script>(function() { var datepicker = $.fn.datepicker.noConflict(); $.fn.bsDatepicker = datepicker; })();</script>"
  )


def selectize_deps() -> html_dependency:
  return html_dependency(
    name = "selectize",
    version = "0.12.6",
    package = "shiny",
    src = "www/shared/selectize",
    script = [
      "js/selectize.min.js",
      "accessibility/js/selectize-plugin-a11y.min.js"
    ],
    # TODO: pre-compile the Bootstrap 5 version?
    stylesheet = "css/selectize.bootstrap3.css"
  )

def jqui_deps() -> html_dependency:
  return html_dependency(
    name = "jquery-ui",
    version = "1.12.1",
    package = "shiny",
    src = "www/shared/jquery-ui",
    script = "jquery-ui.min.js",
    stylesheet = "jquery-ui.min.css"
  )
