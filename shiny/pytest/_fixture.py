from __future__ import annotations

from pathlib import PurePath
from typing import Literal, Union

import pytest

from .._docstring import no_example
from ..run._run import shiny_app_gen

__all__ = (
    "create_app_fixture",
    "ScopeName",
)


ScopeName = Literal["session", "package", "module", "class", "function"]


@no_example()
def create_app_fixture(
    app: Union[PurePath, str],
    scope: ScopeName = "module",
):
    """
    Create a fixture for a local Shiny app directory.

    Parameters
    ----------
    app
        The path to the Shiny app file.
    scope
        The scope of the fixture.
    """

    @pytest.fixture(scope=scope)
    def fixture_func():
        sa_gen = shiny_app_gen(app)
        yield next(sa_gen)

    return fixture_func
