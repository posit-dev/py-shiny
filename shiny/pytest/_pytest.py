from __future__ import annotations

from pathlib import PurePath
from typing import Generator

import pytest

from ..run import ShinyAppProc
from ..run._run import shiny_app_gen
from ..testserver import TestServerSession, test_server


@pytest.fixture(scope="module")
def local_app(request: pytest.FixtureRequest) -> Generator[ShinyAppProc, None, None]:
    """
    Create a local Shiny app for testing.

    The app is launched in Shiny test mode (``SHINY_TESTMODE=1``), enabling the
    `AppTestValues` controller.

    Parameters:
        request (pytest.FixtureRequest): The request object for the fixture.
    """
    # Get the app_file from the parametrize marker if available
    app_file = getattr(request, "param", "app.py")
    sa_gen = shiny_app_gen(
        PurePath(request.path).parent / app_file,
        env={"SHINY_TESTMODE": "1"},
    )
    yield next(sa_gen)


@pytest.fixture(scope="function")
def local_server(
    request: pytest.FixtureRequest,
) -> Generator[TestServerSession, None, None]:
    """
    Run a local Shiny app in memory for testing, via `shiny.testserver.test_server`.

    The app file defaults to ``app.py`` next to the test file, like `local_app`, and
    can be pointed elsewhere with an indirect parametrization::

        @pytest.mark.parametrize("local_server", ["other_app.py"], indirect=True)
        def test_other_app(local_server):
            ...

    Unlike `local_app`, this fixture is function-scoped: a session holds the inputs
    set so far, so sharing one across tests would let them affect each other.

    Parameters:
        request (pytest.FixtureRequest): The request object for the fixture.
    """
    app_file = getattr(request, "param", "app.py")
    # An absolute `Path` (not `PurePath`) so `test_server()` uses it as-is instead of
    # resolving it against *this* file's directory.
    with test_server(request.path.parent / app_file) as session:
        yield session
