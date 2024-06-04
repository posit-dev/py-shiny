from __future__ import annotations

from pathlib import PurePath
from typing import Generator

import pytest

from ..run import ShinyAppProc
from ..run._run import shiny_app_gen


@pytest.fixture(scope="module")
def local_app(request: pytest.FixtureRequest) -> Generator[ShinyAppProc, None, None]:
    """
    Create a local Shiny app for testing.

    Parameters:
        request (pytest.FixtureRequest): The request object for the fixture.
    """
    sa_gen = shiny_app_gen(PurePath(request.path).parent / "app.py")
    yield next(sa_gen)
