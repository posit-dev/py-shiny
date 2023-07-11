import htmltools

from shiny import App, ui
from shiny._app import html_dep_name


def test_duplicate_deps():
    some_dep1 = htmltools.HTMLDependency(
        "test_dep",
        "1",
        source={
            "subdir": ".",
        },
        all_files=True,
    )
    some_dep2 = htmltools.HTMLDependency(
        "test_dep",
        "2",
        source={
            "subdir": ".",
        },
        all_files=True,
    )
    some_dep3 = htmltools.HTMLDependency(
        "test_dep",
        "3",
        source={
            "subdir": ".",
        },
        all_files=True,
    )

    # Put v1 at the end to make sure lower versions can be added
    # Put v3 in the middle to make sure a higher version can be added
    deps = [some_dep2, some_dep3, some_dep1]

    app = App(ui.div("ui goes here"), server=None)

    # During a page refresh, the same session is kept alive. This means the mapping of `app._registered_dependencies` is kept. However, the dependencies requested by the user can be different when using a UI function.

    # Simulate adding the _conflicting_ dependencies from three different dynamic UI
    # functions
    for dep in deps:
        app._register_web_dependency(dep)
    # All three dependencies should be registered as they are unique and will be requested by the browser
    for dep in deps:
        assert html_dep_name(dep) in app._registered_dependencies
