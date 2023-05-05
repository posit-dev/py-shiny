from __future__ import annotations

from pathlib import PurePath

from htmltools import HTMLDependency

from shiny import __version__ as shiny_package_version

ex_www_path = PurePath(__file__).parent.parent / "www"


def card_full_screen_dependency() -> HTMLDependency:
    return HTMLDependency(
        name="bslib-card-full-screen",
        version=shiny_package_version,
        source={
            "package": "shiny",
            "subdir": str(ex_www_path),
        },
        script={"src": "card-full-screen.js"},
    )


def fill_dependency() -> HTMLDependency:
    return HTMLDependency(
        "htmltools-fill",
        "0.0.0.0",
        source={
            "package": "shiny",
            "subdir": str(ex_www_path),
        },
        stylesheet={"href": "fill.css"},
    )


def sidebar_dependency() -> HTMLDependency:
    return HTMLDependency(
        "bslib-sidebar",
        "0.0.0",
        source={
            "package": "shiny",
            "subdir": str(ex_www_path / "sidebar"),
        },
        script={"src": "sidebar.min.js"},
    )


def accordion_dependency() -> HTMLDependency:
    return HTMLDependency(
        "bslib-accordion",
        version=shiny_package_version,
        source={
            "package": "shiny",
            "subdir": str(ex_www_path / "accordion"),
        },
        script={"src": "accordion.min.js"},
    )
