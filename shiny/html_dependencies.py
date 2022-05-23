from htmltools import HTMLDependency


def shiny_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny",
        version="0.0.1",
        source={"package": "shiny", "subdir": "www/shared/"},
        script={"src": "shiny.js"},
        stylesheet={"href": "shiny.min.css"},
    )


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
