# This file is necessary for pytest to find relative module files
# such as examples/example_apps.py

from __future__ import annotations

from pathlib import PurePath

from shiny.test.fixture import ScopeName, create_app_fixture

__all__ = (
    "create_doc_example_fixture",
    "create_example_fixture",
    "create_doc_example_core_fixture",
    "create_doc_example_express_fixture",
)


here = PurePath(__file__).parent
here_root = here.parent.parent


def create_example_fixture(
    example_name: str,
    example_file: str = "app.py",
    scope: ScopeName = "module",
):
    """Used to create app fixtures from apps in py-shiny/examples"""
    return create_app_fixture(
        here_root / "examples" / example_name / example_file, scope
    )


def create_doc_example_fixture(
    example_name: str,
    example_file: str = "app.py",
    scope: ScopeName = "module",
):
    """Used to create app fixtures from apps in py-shiny/shiny/api-examples"""
    return create_app_fixture(
        here_root / "shiny/api-examples" / example_name / example_file, scope
    )


def create_doc_example_core_fixture(
    example_name: str,
    scope: ScopeName = "module",
):
    """Used to create app fixtures from ``app-core.py`` example apps in py-shiny/shiny/api-examples"""
    return create_doc_example_fixture(example_name, "app-core.py", scope)


def create_doc_example_express_fixture(
    example_name: str,
    scope: ScopeName = "module",
):
    """Used to create app fixtures from ``app-express.py`` example apps in py-shiny/shiny/api-examples"""
    return create_doc_example_fixture(example_name, "app-express.py", scope)
