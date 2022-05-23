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


# N.B. py-shiny has requirejs as a 'core' dependency since it's currently a pretty
# fundamental dependency for any Jupyter widget project (i.e., ipyshiny) and we need a
# custom setup for it to work decently with HTMLDependency() model (i.e., loading JS via
# <script> tags). At the moment, we're just setting window.define.amd=false after loading
# requirejs so that the typical UMD pattern won't result in an anonymous define() error.
def require_deps() -> HTMLDependency:
    return HTMLDependency(
        name="requirejs",
        version="2.3.6",
        source={"package": "shiny", "subdir": "www/shared/requirejs/"},
        script={"src": "require.min.js"},
    )
