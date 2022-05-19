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
# fundamental dependency for any Jupyter widget project (i.e., ipyshiny). And, for
# requirejs to work at all with our HTMLDependency() model (i.e., loading JS via
# <script> tags), we need to shim define() to avoid anonymous module errors
def require_deps() -> HTMLDependency:
    return HTMLDependency(
        name="requirejs",
        version="2.3.6",
        source={"package": "shiny", "subdir": "www/shared/requirejs/"},
        script=[{"src": "require.min.js"}, {"src": "define-shim.js"}],
    )
