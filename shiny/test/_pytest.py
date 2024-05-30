from __future__ import annotations

from pathlib import PurePath
from typing import Generator

import pytest

from ._conftest import ShinyAppProc


@pytest.fixture(scope="module")
def local_app(request: pytest.FixtureRequest) -> Generator[ShinyAppProc, None, None]:
    """
    Create a local Shiny app for testing.

    Parameters:
        request (pytest.FixtureRequest): The request object for the fixture.
    """
    app_gen = local_app_fixture_gen(PurePath(request.path).parent / "app.py")
    yield next(app_gen)
