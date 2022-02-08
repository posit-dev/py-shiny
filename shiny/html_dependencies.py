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
