from __future__ import annotations

import inspect
from pathlib import Path, PurePath
from typing import Literal, Union

import pytest

from .._docstring import no_example
from ..run._run import shiny_app_gen
from ..types import MISSING, MISSING_TYPE

__all__ = (
    "create_app_fixture",
    "ScopeName",
)


ScopeName = Literal["session", "package", "module", "class", "function"]


@no_example()
def create_app_fixture(
    app: Union[PurePath, str],
    scope: ScopeName = "module",
    # *,
    # start_dir: Union[PurePath, str, MISSING_TYPE, None] = MISSING,
):
    """
    Create a fixture for a local Shiny app directory.

    Parameters
    ----------
    app
        The path to the Shiny app file.

        If `app` is a `Path` or `PurePath` instance and `.is_file()` returns `True`, then this value will be used directly.
        Note, file paths will be checked from where `pytest` was called, not from the calling function.

        Otherwise, all `app` paths will be considered to be relative paths from where the test function was collected.

        To be sure that your app path is always relative, supply a `str` value.
    scope
        The scope of the fixture.
    """

    @pytest.fixture(scope=scope)
    def fixture_func(request: pytest.FixtureRequest):
        app_purepath_exists = isinstance(app, PurePath) and Path(app).is_file()
        app_path = app if app_purepath_exists else request.path.parent / app
        sa_gen = shiny_app_gen(app_path)
        yield next(sa_gen)

    return fixture_func
